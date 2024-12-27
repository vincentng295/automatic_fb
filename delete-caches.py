import os
import requests

# GitHub repository details
repo = os.getenv("GITHUB_REPOSITORY")
token = os.getenv("GITHUB_TOKEN")
cache_name = os.getenv("CACHE_NAME")

# GitHub API URL for listing caches
api_url = f"https://api.github.com/repos/{repo}/actions/caches"

# Headers for authentication
headers = {
    "Authorization": f"token {token}"
}

def get_fallback_cache_ids():
    """Get IDs of caches with the key 'cookies-cache-' (fallback caches)."""
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  # Ensure we raise an exception for HTTP errors
    
    # Get the cache IDs for fallback caches (those without hashes)
    caches = response.json()
    fallback_cache_ids = [
        cache['id'] for cache in caches.get('actions_caches', [])
        if cache['key'] == cache_name
    ]
    return fallback_cache_ids

def delete_cache(cache_id):
    """Delete a cache by ID."""
    delete_url = f"{api_url}/{cache_id}"
    response = requests.delete(delete_url, headers=headers)
    if response.status_code == 204:
        print(f"Cache {cache_id} deleted successfully.")
    else:
        print(f"Failed to delete cache {cache_id}. Status code: {response.status_code}")

def main():
    fallback_cache_ids = get_fallback_cache_ids()
    if not fallback_cache_ids:
        print("No fallback caches found.")
    else:
        for cache_id in fallback_cache_ids:
            delete_cache(cache_id)

if __name__ == "__main__":
    main()