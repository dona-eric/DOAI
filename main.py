def main():
    from transformers import pipeline
    
    
    generator = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-360M")
    prompt = """
    In this course, we will teach you how to"""

    result = generator(
        prompt=prompt,
        max_length=30,
        num_return_sequences=2,
    )
    print(result[0]['generated_text'])


if __name__ == "__main__":
    main()
