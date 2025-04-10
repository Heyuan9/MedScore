import os
from utils import process_claim
# set os environment variables
os.environ["OPENAI_API_KEY"] = "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"
from openai import OpenAI
TEXT_KEY='doctor_response'
data_file ="/home/hhuan134/scr4_mdredze1/medic_project/data/doctor_responses/fixed_doctor_responses.jsonl"
# data_file ="/home/hhuan134/scr4_mdredze1/medic_project/data/PUMA/PUMA_separated_answers.jsonl"
import json
# read in the json lines file
data = []
with open(data_file, "r") as f:
    for line in f:
        data.append(json.loads(line))
# print(data[0])
# in each item, the key ['answer] is the sentence that needs to be fact checked. Parse it into sentences using spacy
import spacy
nlp = spacy.load("en_core_web_sm")
from spacy.lang.en import English
# Create the nlp object
# parse the sentence into sentences
def parse_sentence(sentence):
    doc = nlp(sentence)
    sentences = [sent.text for sent in doc.sents]
    return sentences

# print(parse_sentence(data[0][TEXT_KEY]))

prompt_file="/home/hhuan134/scr4_mdredze1/hhuan134/MEDIC/GPT/prompts/MedFact_decontext.txt"
# prompt_file="/home/hhuan134/scr4_mdredze1/hhuan134/MEDIC_repo/MEDIC/prompts/FactScore_prompt.txt"
with open(prompt_file, 'r') as file:
    system_prompt = file.read()
# print(system_prompt)

# output_file = "/home/hhuan134/scr4_mdredze1/hhuan134/MEDIC/GPT/results/PUMA/PUMA_medscore-decontext_gpt.jsonl"
# output_file = "/home/hhuan134/scr4_mdredze1/hhuan134/MEDIC/GPT/results/doctor_response_baseline/doctor_medscore-decontext_gpt.jsonl"
output_file = "/home/hhuan134/scr4_mdredze1/hhuan134/MEDIC/GPT/results/doctor_response_baseline/doctor_factscore_gpt.jsonl"
for item in data:
    all_claims = []
    sentences = parse_sentence(item[TEXT_KEY])
    for sentence in sentences:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
        # this is the factscore prompt, with no context key.
                # {"role": "system", "content": system_prompt},
                # {
                #     "role": "user",
                #     "content": f"Please breakdown the following sentence into independent facts: {sentence}"
                # }
        # this is the medscore prompt with context key.
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Context: {item[TEXT_KEY]}\nPlease breakdown the following sentence into independent facts: {sentence}\nFacts:\n"
                }
            ],
            # max_tokens=512,
            temperature=0.0,
        )
        claim_list = completion.choices[0].message.content.split("\n")
        claim_list = process_claim(claim_list)
        all_claims.append(claim_list)
    results = {'id':item['id'],'claims':all_claims}
    with open(output_file, "a") as f:
        f.write(json.dumps(results) + "\n")