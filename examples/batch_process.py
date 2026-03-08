"""
Example: Batch process multiple blog posts
"""

from podcast_generator_ollama import PodcastGeneratorOllama
import os
import json
from datetime import datetime

def batch_generate_podcasts(blogs_file, output_dir="batch_output"):
    """
    Generate podcasts for multiple blogs from a JSON file
    
    Args:
        blogs_file: Path to JSON file with blog data
        output_dir: Directory to save generated podcasts
    """
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load blogs
    with open(blogs_file, 'r', encoding='utf-8') as f:
        blogs = json.load(f)
    
    # Initialize generator
    generator = PodcastGeneratorOllama(model="llama2")
    
    # Track results
    results = {
        'total': len(blogs),
        'successful': 0,
        'failed': 0,
        'details': []
    }
    
    print(f"\n{'='*60}")
    print(f"Batch Processing {len(blogs)} Blogs")
    print(f"{'='*60}\n")
    
    # Process each blog
    for i, blog in enumerate(blogs, 1):
        print(f"[{i}/{len(blogs)}] Processing: {blog.get('title', 'Untitled')}")
        
        try:
            # Generate podcast
            result = generator.generate_podcast(
                blog_content=blog['content'],
                title=blog.get('title', f'Podcast_{i}'),
                podcast_type=blog.get('type', 'single'),
                audience=blog.get('audience', 'global')
            )
            
            if result['success']:
                # Save script
                filename = f"{blog.get('title', f'podcast_{i}').replace(' ', '_')}.txt"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(result['script'])
                
                results['successful'] += 1
                results['details'].append({
                    'title': blog.get('title'),
                    'status': 'success',
                    'file': filepath
                })
                
                print(f"  ✓ Success: {filepath}")
            else:
                results['failed'] += 1
                results['details'].append({
                    'title': blog.get('title'),
                    'status': 'failed',
                    'error': result.get('error')
                })
                print(f"  ✗ Failed: {result.get('error')}")
        
        except Exception as e:
            results['failed'] += 1
            results['details'].append({
                'title': blog.get('title'),
                'status': 'error',
                'error': str(e)
            })
            print(f"  ✗ Error: {str(e)}")
        
        print()
    
    # Save summary
    summary_file = os.path.join(output_dir, f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Batch Processing Complete")
    print(f"{'='*60}")
    print(f"Total:      {results['total']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed:     {results['failed']}")
    print(f"Summary:    {summary_file}")
    print(f"{'='*60}\n")
    
    return results


if __name__ == "__main__":
    # Example blogs data
    example_blogs = [
        {
            "title": "AI in Healthcare",
            "content": "Artificial intelligence is revolutionizing healthcare with early disease detection and personalized treatment plans.",
            "type": "single",
            "audience": "global"
        },
        {
            "title": "Climate Change Solutions",
            "content": "Renewable energy and sustainable practices are key to combating climate change and protecting our planet.",
            "type": "co-host",
            "audience": "global"
        },
        {
            "title": "Indian Startup Ecosystem",
            "content": "India's startup scene is booming with unicorns emerging and innovation thriving across sectors.",
            "type": "co-host",
            "audience": "indian"
        }
    ]
    
    # Save example blogs
    with open('example_blogs.json', 'w', encoding='utf-8') as f:
        json.dump(example_blogs, f, indent=2)
    
    print("Example blogs saved to: example_blogs.json")
    print("\nTo process, run:")
    print("  python batch_process.py")
    print("\nOr use in your code:")
    print("  from batch_process import batch_generate_podcasts")
    print("  batch_generate_podcasts('example_blogs.json')")
