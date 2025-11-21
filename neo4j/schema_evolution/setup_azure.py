"""
Helper script to set up Azure OpenAI credentials
Extracts information from your Azure AI URL
"""

import os

def extract_from_url(url):
    """Extract Azure information from Azure AI URL"""
    print("="*70)
    print("Azure OpenAI Credential Extractor")
    print("="*70)

    # Parse the URL
    if "accounts/" in url and "projects/" in url:
        # Extract account name
        account = url.split("accounts/")[1].split("/")[0]
        print(f"\n✓ Found Azure Account: {account}")

        # Extract project name
        project = url.split("projects/")[1].split("&")[0].split("?")[0]
        print(f"✓ Found Project: {project}")

        # Extract model name from URL
        if "models/" in url:
            model_info = url.split("models/")[1].split("/")[0]
            print(f"✓ Found Model: {model_info}")

        # Construct likely endpoint
        endpoint = f"https://{account}.openai.azure.com/"
        print(f"\n📍 Likely Endpoint: {endpoint}")

        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)

        print("\n1. Get your API Key:")
        print("   Go to: https://portal.azure.com/")
        print(f"   Navigate to: Cognitive Services > {account}")
        print("   Click: 'Keys and Endpoint' in left menu")
        print("   Copy: Key 1 or Key 2")

        print("\n2. Get your Deployment Name:")
        print("   Go to: https://ai.azure.com/")
        print(f"   Navigate to: Projects > {project} > Deployments")
        print("   Note the exact deployment name (e.g., 'gpt-4', 'gpt-oss-120B')")

        print("\n3. Update your .env file:")
        print(f"""
cat > .env << 'EOF'
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT={endpoint}
AZURE_OPENAI_API_KEY=your_api_key_here  # Replace with actual key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4  # Replace with your deployment name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Neo4j (already configured)
NEO4J_URL=neo4j+s://d0d1fe15.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=QR9Xqoy0bdfPVSB77hqO-cHZwaouDYUJW43CU6gYKGA
NEO4J_DATABASE=neo4j
EOF
""")

        print("\n4. Edit the .env file to add your actual API key:")
        print("   nano .env")

        print("\n5. Run the system:")
        print("   python main.py --iterations 2")

        print("\n" + "="*70)

    else:
        print("\n❌ Could not parse URL. Please provide your credentials manually.")
        print("\nCreate a .env file with:")
        print("""
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
""")


if __name__ == "__main__":
    # URL from user
    url = "https://ai.azure.com/resource/models/gpt-oss-120B/version/4/registry/azureml-openai-oss?wsid=/subscriptions/c1e4af85-aede-4544-9e15-9beef8836b0e/resourceGroups/hi/providers/Microsoft.CognitiveServices/accounts/smith/projects/firstProject&tid=2930a3f8-0838-4b56-80fe-e30e7a91ee89"

    extract_from_url(url)
