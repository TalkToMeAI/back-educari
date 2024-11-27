import argparse
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.embeddings.bedrock import BedrockEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage,SystemMessage  # Importa las clases necesarias
import redis  
from dotenv import load_dotenv
import openai
import os

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
    Eres un profesor de matemáticas que enseña a un estudiante de 16 años. Tu tarea es explicar el siguiente tema de manera clara, sencilla y con ejemplos prácticos, asegurándote de que el estudiante pueda comprenderlo fácilmente. La explicación debe estar en español y debe estar orientada a alguien que está comenzando a aprender este concepto.


    Contexto:
    {context}

    ---

    Pregunta: {question}



"""

PROMPT_TEMPLATE_INTRO = """
Eres un profesor de matemáticas que enseña a un estudiante de 16 años. Tu tarea es explicar el siguiente tema de manera clara, sencilla y con ejemplos prácticos, asegurándote de que el estudiante pueda comprenderlo fácilmente. La explicación debe estar en español y debe estar orientada a alguien que está comenzando a aprender este concepto.


Contexto:
{context}

---


Instrucciones para la introducción:
1. Explica qué son los **números enteros** de forma simple, destacando la diferencia entre los **números enteros positivos** y **negativos**.
2. Usa ejemplos de la vida diaria (como temperaturas, deudas, etc.) para mostrar cómo los números enteros se utilizan en situaciones cotidianas.
3. Menciona la importancia de los números enteros en las matemáticas y cómo se utilizan en operaciones básicas como la suma, resta, multiplicación y división.
4. Asegúrate de que el estudiante entienda por qué los números enteros son esenciales para resolver una variedad de problemas matemáticos.

Introducción sugerida: 
"""

class RAGQueryHandler:
    def __init__(self, chroma_path: str = CHROMA_PATH, embedding_type: str = "openai"):
        self.chroma_path = chroma_path
        self.embedding_function = self.get_embedding_function(embedding_type)
        # Asegúrate de pasar la función de embeddings al inicializar Chroma
        self.db = Chroma(persist_directory=self.chroma_path, embedding_function=self.embedding_function)

    def get_embedding_function(self, embedding_type: str):
        if embedding_type == "bedrock":
            return BedrockEmbeddings(credentials_profile_name="default", region_name="us-east-1")
        elif embedding_type == "ollama":
            return OllamaEmbeddings()  
        elif embedding_type == "openai":
            return OpenAIEmbeddings()
        else:
            raise ValueError(f"Unknown embedding type: {embedding_type}")

    def query_rag(self, user_id: str, query_text: str, model_name: str = "gpt-3.5-turbo"):
        historial = redis_client.get(user_id)
        counter_question = redis_client.get(f"{user_id}_counter_question")
        status = redis_client.get(f"{user_id}_status")

        if status is None:
            status = "intro"
            redis_client.set(f"{user_id}_status", status)

        #if status == "intro":
            #question = f"Realiza una introducción al tema de los números enteros "
        #if status == "practice":
            #question = f"Realiza un ejercicio de los números enteros "
        #if status == "theory":
            #question = f"Realiza una teoría de los números enteros "
        #if status == "challenge":
            #question = f"Realiza un desafío de los números enteros "
        #if status == "review":
            #question = f"Realiza un repaso de los números enteros "
        
            

        if counter_question is None:
            counter_question = 0
        else:
            counter_question = int(counter_question)
        counter_question += 1
        
        if counter_question == 2:
            status = "practice"
            redis_client.set(f"{user_id}_status", status)
        if counter_question == 3:
            status = "theory"
            redis_client.set(f"{user_id}_status", status)
        if counter_question == 4:
            status = "challenge"
            redis_client.set(f"{user_id}_status", status)
        if counter_question == 5:
            status = "review"
            redis_client.set(f"{user_id}_status", status)
        
        redis_client.set(f"{user_id}_counter_question", counter_question)
        print("counter_question", counter_question)
        print("status", status)
        
        results = self.db.similarity_search_with_score(query_text, k=5)
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
        
        ##if historial:
        #historial_data = eval(historial)
        #messages = historial_data["messages"]
        #context_text = "\n\n---\n\n".join([msg["content"] for msg in messages])
        #else:
        
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=status)
        model = ChatOpenAI()
        

        messages = [
            SystemMessage(content="Realiza una introducción para los números enteros, conversa como si fueras un profesor de matemáticas, y no contestes preguntas que no sean del tema"),
            HumanMessage(content="Hola me puedes hacer una recopilación de matereia para orientarme?   "),
        ]

        response_text = model.invoke(prompt)
        
        memory = ConversationBufferMemory()
        #conversation_chain = ConversationChain(llm=model, memory=memory)
        
        historial = redis_client.get(user_id)
        if historial:
            historial_data = eval(historial) 
            messages = historial_data["messages"]
            memory.chat_memory.messages = [
                HumanMessage(content=msg["content"]) if msg["type"] == "human" else AIMessage(content=msg["content"]) 
                for msg in messages
            ]
        
        memory.chat_memory.add_user_message(query_text)
        
        #respuesta = conversation_chain.invoke(input=prompt)
        
        history_with_sources = {
            "messages": [{"type": "human", "content": msg.content} if isinstance(msg, HumanMessage) else {"type": "ai", "content": msg.content} 
                         for msg in memory.chat_memory.messages],
            "sources": [doc.metadata.get("id", None) for doc, _score in results]
        }
        
        redis_client.set(user_id, str(history_with_sources)) 

        #sources = [doc.metadata.get("id", None) for doc, _score in results]
        #formatted_response = f"Response: {response_text}\nSources: {sources}"
        return response_text
    def query_gpt(self, user_id: str, query_text: str, student_name: str, model_name: str = "gpt-3.5-turbo"):
        # Obtener datos del usuario desde Redis
        counter_question = redis_client.get(f"{user_id}_counter_question")
        historial = redis_client.get(f"{user_id}_history")

        # Inicializar valores si no existen
        if counter_question is None:
            counter_question = 0
        else:
            counter_question = int(counter_question)

        # Manejar historial del chat
        if historial:
            try:
                messages = eval(historial)  # Recuperar historial como lista de mensajes
            except Exception as e:
                print(f"Error al cargar el historial: {e}")
                messages = []
        else:
            messages = []

        # Añadir mensaje del sistema inicial si el historial está vacío
        intro_message = (
            f"Eres un profesor de matemáticas. Responde únicamente sobre números enteros. El nombre del usuario es {student_name}."
            f" Alterna entre explicar conceptos (texto) y hacer preguntas prácticas (tipo pregunta con opciones)."
        )
        if len(messages) == 0:
            messages.insert(0, {"role": "system", "content": intro_message})

        # Añadir el mensaje del usuario
        messages.append({"role": "user", "content": query_text})

        # Crear modelo GPT y generar respuesta
        model = ChatOpenAI(model_name=model_name)
        try:
            response = model(messages)
            response_text = response.content.strip()
        except Exception as e:
            print(f"Error al obtener respuesta del modelo: {e}")
            response_text = "Lo siento, hubo un error al procesar tu consulta. Intenta de nuevo."
            response = None

        # Actualizar historial con la respuesta del asistente
        if response:
            messages.append({"role": "assistant", "content": response_text})
            redis_client.set(f"{user_id}_history", str(messages))

        # Alternar entre texto y pregunta basándonos en el contador
        counter_question += 1
        redis_client.set(f"{user_id}_counter_question", counter_question)

        if counter_question % 2 == 0:  # Pregunta (type: "question")
            # Generar opciones relevantes para la pregunta
            options_prompt = (
                f"Basándote en la siguiente pregunta generada, crea 3 opciones de respuesta: {response_text}.\n"
                "Incluye una opción correcta y dos incorrectas plausibles. Las opciones deben estar etiquetadas como a), b), y c)."
            )
            try:
                options_response = model([
                    {"role": "system", "content": intro_message},
                    {"role": "user", "content": options_prompt}
                ])
                raw_options = options_response.content.strip().split("\n")
                options = [option.strip() for option in raw_options if option.strip()]

                # Validar que las opciones incluyan "a)", "b)", y "c)"
                if not all(opt.startswith(("a)", "b)", "c)")) for opt in options[:3]):
                    raise ValueError("Opciones generadas no tienen el formato esperado.")

            except Exception as e:
                print(f"Error al generar opciones: {e}")
                options = [
                    "a) Opción correcta",
                    "b) Opción incorrecta 1",
                    "c) Opción incorrecta 2"
                ]  # Opciones de fallback

            formatted_response = {
                "id": counter_question,
                "text": response_text,
                "type": "question",
                "sender": "agent",
                "options": options[:3]  # Asegurarse de que no haya más de 3 opciones
            }
        else:  # Texto explicativo (type: "text")
            formatted_response = {
                "id": counter_question,
                "text": response_text,
                "type": "text",
                "sender": "agent"
            }

        return formatted_response




    def query_combined(self, user_id: str, query_text: str, model_name: str = "gpt-3.5-turbo"):
        # Obtener estado y contador de preguntas desde Redis
        counter_question = redis_client.get(f"{user_id}_counter_question")
        status = redis_client.get(f"{user_id}_status")

        if status is None:
            status = "intro"
            redis_client.set(f"{user_id}_status", status)

        # Actualizar el contador de preguntas
        if counter_question is None:
            counter_question = 0
        else:
            counter_question = int(counter_question)
        counter_question += 1

        # Cambiar el estado basado en el contador de preguntas
        if counter_question == 2:
            status = "practice"
        elif counter_question == 3:
            status = "theory"
        elif counter_question == 4:
            status = "challenge"
        elif counter_question == 5:
            status = "review"

        redis_client.set(f"{user_id}_counter_question", counter_question)
        redis_client.set(f"{user_id}_status", status)

        # Recuperar el contexto desde RAG
        results = self.db.similarity_search_with_score(query_text, k=5)
        context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

        # Crear el modelo GPT y el prompt combinado
        model = ChatOpenAI(model_name=model_name)
        messages = [
            SystemMessage(content=(
                "Eres un profesor de matemáticas experto en números enteros. Utiliza la información del contexto cuando sea relevante,Pensado para alumno de 1ero medio 17 años"
                "y responde de manera detallada y clara. Si no encuentras la respuesta en el contexto, utiliza tus conocimientos generales."
            )),
            HumanMessage(content=f"Contexto relevante:\n{context_text}\n\nPregunta: {query_text}")
        ]

        # Generar respuesta
        response = model(messages)

        # Actualizar historial en Redis
        historial = redis_client.get(user_id)
        if historial:
            historial_data = eval(historial)
            messages = historial_data["messages"]
        else:
            messages = []

        # Añadir la consulta y la respuesta al historial
        messages.append({"type": "human", "content": query_text})
        messages.append({"type": "ai", "content": response.content})

        redis_client.set(user_id, str({"messages": messages}))

        return response.content
