from langchain_openai import OpenAIEmbeddings
from langchain.evaluation import load_evaluator
from dotenv import load_dotenv
import openai
import os

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']

def create_ascii_chart(results):
    max_length = 30  
    chart_lines = []
    
    chart_lines.append("|---------------------------|")
    chart_lines.append(f"|   Similaridad a '{comparison_word}'  |")
    chart_lines.append("|---------------------------|")
    
    for word1, _, score in results:
        bar_length = int(score * max_length) 
        bar = "█" * bar_length
        chart_lines.append(f"| {word1:<7} | {bar:<{max_length}} {score:.4f} |")
    
    chart_lines.append("|---------------------------|")
    return "\n".join(chart_lines)

def main():
    global comparison_word
    comparison_word = "Music"
    
    embedding_function = OpenAIEmbeddings()
    vector = embedding_function.embed_query(comparison_word)
    vector_length = len(vector)

    evaluator = load_evaluator("pairwise_embedding_distance")

    words_to_compare = [("pear", comparison_word), ("fruits", comparison_word), ("orange", comparison_word), ("dance", comparison_word)]
    
    results = []
    
    for word1, word2 in words_to_compare:
        score = evaluator.evaluate_string_pairs(prediction=word1, prediction_b=word2)
        results.append((word1, word2, score['score']))
    
    md_content = f"# Resultados de Comparación de Embeddings\n\n"
    md_content += f"## Longitud del vector para '{comparison_word}': {vector_length}\n\n"
    
    ascii_chart = create_ascii_chart(results)
    md_content += ascii_chart + "\n"

    with open("../test/embedding_comparisons2.md", "w") as f:
        f.write(md_content)
    
    print("Resultados guardados en test/embedding_comparisons.md")

if __name__ == "__main__":
    main()
