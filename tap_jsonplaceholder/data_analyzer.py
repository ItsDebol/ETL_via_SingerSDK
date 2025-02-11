"""data_analyzer.py"""
import json
from collections import defaultdict, Counter
from typing import List, Dict
import statistics
from pathlib import Path
import re
from datetime import datetime

class JSONPlaceholderAnalyzer:
    def __init__(self):
        self.users = {}
        self.posts = []
        self.comments = []
        self.metrics = {}
        
    def load_data(self, filename='output.json'):
        """Load and parse the Singer tap output."""
        current_dir = Path(__file__).parent
        filepath = current_dir / filename
        
        print(f"Attempting to read from: {filepath}")
        
        if not filepath.exists():
            print(f"Error: File not found at {filepath}")
            return False
        
        # Try different encodings
        encodings = ['utf-8', 'utf-16', 'utf-16le', 'utf-16be', 'latin-1']
        
        for encoding in encodings:
            try:
                print(f"\nTrying {encoding} encoding...")
                with open(filepath, 'r', encoding=encoding) as f:
                    print("Successfully opened file")
                    line_count = 0
                    for line in f:
                        try:
                            message = json.loads(line.strip())
                            if message['type'] == 'RECORD':
                                if message['stream'] == 'users':
                                    self.users[message['record']['id']] = message['record']
                                elif message['stream'] == 'posts':
                                    self.posts.append(message['record'])
                                elif message['stream'] == 'comments':
                                    self.comments.append(message['record'])
                            line_count += 1
                            if line_count == 1:  # Print first successful message
                                print(f"First message parsed: {message['type']}")
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            print(f"Other error while parsing: {str(e)}")
                            continue
                    
                    print(f"Processed {line_count} lines")
                    print(f"Loaded {len(self.users)} users, {len(self.posts)} posts, {len(self.comments)} comments")
                    return True
                    
            except UnicodeError:
                continue
            except Exception as e:
                print(f"Error with {encoding}: {str(e)}")
                continue
        
        print("Failed to read file with any encoding")
        return False

    def analyze_user_activity(self) -> Dict:
        """Analyze user posting and engagement patterns."""
        if not self.users:
            print("No user data available")
            return {}
            
        user_metrics = defaultdict(lambda: {
            'post_count': 0,
            'total_comments_received': 0,
            'avg_comments_per_post': 0,
            'total_words_in_posts': 0,
            'avg_post_length': 0
        })

        # Analyze posts
        for post in self.posts:
            user_id = post['userId']
            user_metrics[user_id]['post_count'] += 1
            words = len(post['body'].split())
            user_metrics[user_id]['total_words_in_posts'] += words

        # Count comments per post
        post_comments = defaultdict(list)
        for comment in self.comments:
            post_comments[comment['postId']].append(comment)

        # Calculate averages and comment metrics
        for post in self.posts:
            user_id = post['userId']
            comments_count = len(post_comments[post['id']])
            user_metrics[user_id]['total_comments_received'] += comments_count

        # Calculate averages
        for user_id, metrics in user_metrics.items():
            if metrics['post_count'] > 0:
                metrics['avg_comments_per_post'] = metrics['total_comments_received'] / metrics['post_count']
                metrics['avg_post_length'] = metrics['total_words_in_posts'] / metrics['post_count']
                metrics['username'] = self.users.get(user_id, {}).get('username', f'User {user_id}')

        return dict(user_metrics)

    def analyze_comment_patterns(self) -> Dict:
        """Analyze commenting patterns and engagement."""
        if not self.comments:
            print("No comment data available")
            return {
                'total_comments': 0,
                'avg_comment_length': 0,
                'common_email_domains': {},
                'sentiment_indicators': {
                    'positive_words': 0,
                    'negative_words': 0,
                    'question_comments': 0
                },
                'most_common_words': {}
            }

        comment_metrics = {
            'total_comments': len(self.comments),
            'avg_comment_length': 0,
            'common_email_domains': Counter(),
            'comments_by_hour': defaultdict(int),
            'word_frequency': Counter(),
            'sentiment_indicators': {
                'positive_words': 0,
                'negative_words': 0,
                'question_comments': 0
            }
        }

        total_length = 0
        simple_sentiment_pos = {'good', 'great', 'awesome', 'excellent', 'happy', 'thanks'}
        simple_sentiment_neg = {'bad', 'poor', 'terrible', 'awful', 'sad', 'wrong'}

        for comment in self.comments:
            total_length += len(comment['body'])
            email = comment['email'].lower()
            domain = email.split('@')[-1]
            comment_metrics['common_email_domains'][domain] += 1

            words = comment['body'].lower().split()
            comment_metrics['word_frequency'].update(words)

            comment_lower = comment['body'].lower()
            comment_metrics['sentiment_indicators']['positive_words'] += sum(
                1 for word in simple_sentiment_pos if word in comment_lower
            )
            comment_metrics['sentiment_indicators']['negative_words'] += sum(
                1 for word in simple_sentiment_neg if word in comment_lower
            )

            if '?' in comment['body']:
                comment_metrics['sentiment_indicators']['question_comments'] += 1

        if self.comments:
            comment_metrics['avg_comment_length'] = total_length / len(self.comments)
        comment_metrics['common_email_domains'] = dict(comment_metrics['common_email_domains'].most_common(5))
        comment_metrics['most_common_words'] = dict(comment_metrics['word_frequency'].most_common(10))

        return comment_metrics

    def analyze_post_engagement(self) -> Dict:
        """Analyze post engagement patterns."""
        if not self.posts:
            print("No post data available")
            return {
                'total_posts': 0,
                'posts_by_length': {'short': 0, 'medium': 0, 'long': 0},
                'title_length_stats': {'min': 0, 'max': 0, 'avg': 0, 'median': 0},
                'most_engaging_posts': [],
                'engagement_by_user': {}
            }

        post_metrics = {
            'total_posts': len(self.posts),
            'posts_by_length': {
                'short': 0,
                'medium': 0,
                'long': 0
            },
            'title_length_stats': {},
            'most_engaging_posts': [],
            'engagement_by_user': defaultdict(int)
        }

        title_lengths = []
        for post in self.posts:
            words = len(post['body'].split())
            if words < 100:
                post_metrics['posts_by_length']['short'] += 1
            elif words < 200:
                post_metrics['posts_by_length']['medium'] += 1
            else:
                post_metrics['posts_by_length']['long'] += 1
            
            title_lengths.append(len(post['title']))

        if title_lengths:
            post_metrics['title_length_stats'] = {
                'min': min(title_lengths),
                'max': max(title_lengths),
                'avg': statistics.mean(title_lengths),
                'median': statistics.median(title_lengths)
            }
        else:
            post_metrics['title_length_stats'] = {
                'min': 0, 'max': 0, 'avg': 0, 'median': 0
            }

        post_engagement = defaultdict(list)
        for comment in self.comments:
            post_engagement[comment['postId']].append(comment)

        post_engagement_metrics = []
        for post in self.posts:
            engagement = len(post_engagement[post['id']])
            post_engagement_metrics.append({
                'post_id': post['id'],
                'title': post['title'],
                'user_id': post['userId'],
                'comment_count': engagement
            })
            post_metrics['engagement_by_user'][post['userId']] += engagement

        post_metrics['most_engaging_posts'] = sorted(
            post_engagement_metrics,
            key=lambda x: x['comment_count'],
            reverse=True
        )[:5]

        return post_metrics

    def generate_report(self):
        """Generate a comprehensive analysis report."""
        print("\n=== JSONPlaceholder Data Analysis Report ===\n")

        # User Activity Analysis
        user_activity = self.analyze_user_activity()
        if user_activity:
            print("User Activity Insights:")
            print("-----------------------")
            for user_id, metrics in user_activity.items():
                print(f"\nUser: {metrics['username']}")
                print(f"Posts: {metrics['post_count']}")
                print(f"Total Comments Received: {metrics['total_comments_received']}")
                print(f"Avg Comments per Post: {metrics['avg_comments_per_post']:.2f}")
                print(f"Avg Post Length (words): {metrics['avg_post_length']:.2f}")

        # Comment Analysis
        comment_metrics = self.analyze_comment_patterns()
        print("\nComment Patterns:")
        print("----------------")
        print(f"Total Comments: {comment_metrics['total_comments']}")
        print(f"Average Comment Length: {comment_metrics['avg_comment_length']:.2f} characters")
        if comment_metrics['common_email_domains']:
            print("\nTop Email Domains:")
            for domain, count in comment_metrics['common_email_domains'].items():
                print(f"  {domain}: {count}")
        print("\nSentiment Indicators:")
        print(f"  Positive Words: {comment_metrics['sentiment_indicators']['positive_words']}")
        print(f"  Negative Words: {comment_metrics['sentiment_indicators']['negative_words']}")
        print(f"  Questions: {comment_metrics['sentiment_indicators']['question_comments']}")

        # Post Engagement Analysis
        post_metrics = self.analyze_post_engagement()
        if post_metrics['total_posts'] > 0:
            print("\nPost Engagement Insights:")
            print("----------------------")
            print("Post Length Distribution:")
            for category, count in post_metrics['posts_by_length'].items():
                print(f"  {category}: {count}")
            if post_metrics['most_engaging_posts']:
                print("\nMost Engaging Posts:")
                for post in post_metrics['most_engaging_posts']:
                    print(f"  Post {post['post_id']}: {post['title'][:30]}... ({post['comment_count']} comments)")

    def export_to_csv(self):
        """Export analysis results to CSV files."""
        import csv
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export user metrics
        user_activity = self.analyze_user_activity()
        with open(f'user_metrics_{timestamp}.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Username',
                'Post Count',
                'Total Comments Received',
                'Avg Comments per Post',
                'Avg Post Length (words)'
            ])
            for metrics in user_activity.values():
                writer.writerow([
                    metrics['username'],
                    metrics['post_count'],
                    metrics['total_comments_received'],
                    f"{metrics['avg_comments_per_post']:.2f}",
                    f"{metrics['avg_post_length']:.2f}"
                ])
        
        # Export post metrics
        post_metrics = self.analyze_post_engagement()
        with open(f'post_metrics_{timestamp}.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write overall metrics
            writer.writerow(['Post Distribution Statistics'])
            writer.writerow(['Category', 'Count'])
            for category, count in post_metrics['posts_by_length'].items():
                writer.writerow([category, count])
            
            # Write blank row as separator
            writer.writerow([])
            
            # Write engaging posts
            writer.writerow(['Most Engaging Posts'])
            writer.writerow(['Post ID', 'Title', 'Comment Count'])
            for post in post_metrics['most_engaging_posts']:
                writer.writerow([
                    post['post_id'],
                    post['title'],
                    post['comment_count']
                ])
        
        # Export comment metrics
        comment_metrics = self.analyze_comment_patterns()
        with open(f'comment_metrics_{timestamp}.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Comment Statistics'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Comments', comment_metrics['total_comments']])
            writer.writerow(['Average Comment Length', f"{comment_metrics['avg_comment_length']:.2f}"])
            writer.writerow(['Positive Word Count', comment_metrics['sentiment_indicators']['positive_words']])
            writer.writerow(['Negative Word Count', comment_metrics['sentiment_indicators']['negative_words']])
            writer.writerow(['Question Comments', comment_metrics['sentiment_indicators']['question_comments']])
            
            # Write blank row as separator
            writer.writerow([])
            
            # Write email domain statistics
            writer.writerow(['Top Email Domains'])
            writer.writerow(['Domain', 'Count'])
            for domain, count in comment_metrics['common_email_domains'].items():
                writer.writerow([domain, count])
        
        print(f"\nExported analysis results to CSV files:")
        print(f"- user_metrics_{timestamp}.csv")
        print(f"- post_metrics_{timestamp}.csv")
        print(f"- comment_metrics_{timestamp}.csv")

def main():
    analyzer = JSONPlaceholderAnalyzer()
    success = analyzer.load_data()
    if success:
        analyzer.generate_report()
        analyzer.export_to_csv()
    else:
        print("Failed to load data. Please check the file path and contents.")

if __name__ == "__main__":
    main()