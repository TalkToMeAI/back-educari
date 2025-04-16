import openai



def explicar_imagen_usando_vision(recurso, clase):
    """
    Envía una imagen a GPT-4 Vision junto con contexto de clase para obtener una explicación.
    """
    prompt = f"""
Eres un profesor experto en matemáticas para educación media. 
Analiza la siguiente imagen y explica cómo apoya el aprendizaje de la siguiente clase:

Título de la clase: {clase['titulo']}
Descripción: {clase['descripcion']}
Etapa de la clase: {recurso['etapa']}
Descripción del recurso: {recurso['descripcion']}

Explica qué muestra la imagen, cómo se relaciona con el contenido de la clase y qué deberían observar los estudiantes.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": recurso["data"]}}
                ]
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content.strip()
