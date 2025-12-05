from google import genai

client = genai.Client(api_key="AIzaSyC25hfSzRZ4baYv5ExzEs8cwY57OczpmiQ")

print("Available models:\n")

for m in client.models.list():
    print(m.name)
