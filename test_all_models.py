"""
Test CPRA analysis with all 3 target models to compare performance.
"""

import sys
import os
import time
sys.path.append('src')

from processors.cpra_analyzer import CPRAAnalyzer, create_sample_cpra_requests
from parsers.email_parser import EmailParser

def test_all_models():
    """Test all 3 target models for CPRA analysis."""
    models = ['gemma3:latest', 'phi4-mini-reasoning:3.8b', 'gpt-oss:20b']
    
    # Load sample data
    email_parser = EmailParser()
    with open("data/sample_emails/test_emails.txt", 'r') as f:
        emails = email_parser.parse_email_file(f.read())
    
    cpra_requests = create_sample_cpra_requests()
    
    # Take first 3 emails for testing
    test_emails = emails[:3]
    
    results = {}
    
    for model in models:
        print(f"\n{'='*50}")
        print(f"Testing model: {model}")
        print(f"{'='*50}")
        
        try:
            # Initialize analyzer for this model
            analyzer = CPRAAnalyzer(model_name=model)
            
            model_results = {
                'analyses': [],
                'total_time': 0,
                'success_count': 0,
                'error_count': 0
            }
            
            start_time = time.time()
            
            for i, email in enumerate(test_emails):
                print(f"\nAnalyzing email {i+1}: {email.subject[:50]}...")
                
                email_start = time.time()
                analysis = analyzer.analyze_email_responsiveness(email, cpra_requests, i)
                email_time = time.time() - email_start
                
                if analysis:
                    model_results['analyses'].append({
                        'email_subject': email.subject,
                        'responsive_to': analysis.get_responsive_requests(),
                        'confidence': [c.value for c in analysis.confidence],
                        'processing_time': email_time
                    })
                    model_results['success_count'] += 1
                    print(f"  ✓ Success - Responsive to requests: {analysis.get_responsive_requests()}")
                    print(f"  ✓ Processing time: {email_time:.2f}s")
                else:
                    model_results['error_count'] += 1
                    print(f"  ✗ Analysis failed")
            
            model_results['total_time'] = time.time() - start_time
            results[model] = model_results
            
            print(f"\nModel {model} Summary:")
            print(f"  Success rate: {model_results['success_count']}/{len(test_emails)}")
            print(f"  Total time: {model_results['total_time']:.2f}s")
            print(f"  Average time per email: {model_results['total_time']/len(test_emails):.2f}s")
            
        except Exception as e:
            print(f"Error testing model {model}: {e}")
            results[model] = {'error': str(e)}
    
    # Print final comparison
    print(f"\n{'='*70}")
    print("MODEL PERFORMANCE COMPARISON")
    print(f"{'='*70}")
    
    for model, result in results.items():
        if 'error' in result:
            print(f"{model}: ERROR - {result['error']}")
        else:
            success_rate = result['success_count'] / len(test_emails) * 100
            avg_time = result['total_time'] / len(test_emails)
            print(f"{model}:")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Avg Time/Email: {avg_time:.2f}s")
            print(f"  Total Time: {result['total_time']:.2f}s")
            print()

if __name__ == "__main__":
    test_all_models()