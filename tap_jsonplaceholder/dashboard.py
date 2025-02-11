import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import time
from datetime import datetime
import io

class DashboardAnalyzer:
    def __init__(self):
        self.users = {}
        self.posts = []
        self.comments = []
        
    def load_data(self, uploaded_file):
        try:
            # Convert Streamlit's UploadedFile to string content
            stringio = io.StringIO(uploaded_file.getvalue().decode('utf-16'))
            for line in stringio:
                try:
                    message = json.loads(line.strip())
                    if message['type'] == 'RECORD':
                        if message['stream'] == 'users':
                            self.users[message['record']['id']] = message['record']
                        elif message['stream'] == 'posts':
                            self.posts.append(message['record'])
                        elif message['stream'] == 'comments':
                            self.comments.append(message['record'])
                except json.JSONDecodeError:
                    continue
            
            # Show success message
            st.success(f"Successfully loaded {len(self.users)} users, {len(self.posts)} posts, and {len(self.comments)} comments")
            return True
            
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return False

    def get_user_metrics(self):
        user_metrics = []
        for user_id, user in self.users.items():
            user_posts = [post for post in self.posts if post['userId'] == user_id]
            post_count = len(user_posts)
            
            comments_count = sum(len([c for c in self.comments if c['postId'] == post['id']]) for post in user_posts)
            avg_post_length = sum(len(post['body'].split()) for post in user_posts) / post_count if post_count > 0 else 0
            
            user_metrics.append({
                'username': user['username'],
                'post_count': post_count,
                'total_comments': comments_count,
                'avg_post_length': round(avg_post_length, 2)
            })
        return pd.DataFrame(user_metrics)

    def get_post_metrics(self):
        post_metrics = []
        for post in self.posts:
            comment_count = len([c for c in self.comments if c['postId'] == post['id']])
            post_metrics.append({
                'post_id': post['id'],
                'title': post['title'],
                'length': len(post['body'].split()),
                'comment_count': comment_count
            })
        return pd.DataFrame(post_metrics)

    def get_comment_metrics(self):
        comment_lengths = [len(comment['body']) for comment in self.comments]
        return {
            'total_comments': len(self.comments),
            'avg_length': sum(comment_lengths) / len(comment_lengths) if comment_lengths else 0,
            'lengths': comment_lengths
        }

def main():
    st.set_page_config(
        page_title="JSONPlaceholder Analytics Dashboard",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 JSONPlaceholder Analytics Dashboard")
    
    # Initialize analyzer
    analyzer = DashboardAnalyzer()
    
    # File uploader with clear instructions
    st.write("### Upload Data File")
    st.write("Please upload your output.json file (UTF-16 encoded)")
    uploaded_file = st.file_uploader(
        "Drag and drop your file here",
        type=['json'],
        help="Make sure the file is in JSON format and UTF-16 encoded"
    )
    
    if uploaded_file is not None:
        # Add a spinner while loading data
        with st.spinner('Loading and processing data...'):
            if analyzer.load_data(uploaded_file):
                # Create tabs
                tab1, tab2, tab3 = st.tabs(["User Analytics", "Post Analytics", "Comment Analytics"])
                
                # User Analytics Tab
                with tab1:
                    st.header("User Analytics")
                    user_metrics = analyzer.get_user_metrics()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_posts = px.bar(
                            user_metrics, 
                            x='username', 
                            y='post_count',
                            title='Posts per User',
                            color='post_count',
                            color_continuous_scale='Viridis'
                        )
                        st.plotly_chart(fig_posts, use_container_width=True)
                    
                    with col2:
                        fig_comments = px.bar(
                            user_metrics,
                            x='username',
                            y='total_comments',
                            title='Comments Received per User',
                            color='total_comments',
                            color_continuous_scale='Viridis'
                        )
                        st.plotly_chart(fig_comments, use_container_width=True)
                    
                    st.subheader("User Metrics Table")
                    st.dataframe(
                        user_metrics.style.background_gradient(subset=['post_count', 'total_comments']),
                        height=400
                    )
                
                # Post Analytics Tab
                with tab2:
                    st.header("Post Analytics")
                    post_metrics = analyzer.get_post_metrics()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_engagement = px.scatter(
                            post_metrics,
                            x='length',
                            y='comment_count',
                            title='Post Length vs. Engagement',
                            hover_data=['title'],
                            color_discrete_sequence=['#3366cc']
                        )
                        st.plotly_chart(fig_engagement, use_container_width=True)
                    
                    with col2:
                        fig_length_dist = px.histogram(
                            post_metrics,
                            x='length',
                            title='Post Length Distribution',
                            color_discrete_sequence=['#3366cc']
                        )
                        st.plotly_chart(fig_length_dist, use_container_width=True)
                    
                    st.subheader("Top Engaged Posts")
                    top_posts = post_metrics.nlargest(5, 'comment_count')
                    st.dataframe(
                        top_posts[['title', 'comment_count', 'length']].style.background_gradient(subset=['comment_count']),
                        height=300
                    )
                
                # Comment Analytics Tab
                with tab3:
                    st.header("Comment Analytics")
                    comment_metrics = analyzer.get_comment_metrics()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Total Comments",
                            f"{comment_metrics['total_comments']:,}",
                            delta=None
                        )
                    
                    with col2:
                        st.metric(
                            "Average Comment Length",
                            f"{comment_metrics['avg_length']:.2f} characters",
                            delta=None
                        )
                    
                    fig_comment_dist = px.histogram(
                        x=comment_metrics['lengths'],
                        title='Comment Length Distribution',
                        labels={'x': 'Comment Length (characters)', 'y': 'Count'},
                        color_discrete_sequence=['#3366cc']
                    )
                    st.plotly_chart(fig_comment_dist, use_container_width=True)

                # Add refresh button with updated rerun method
                if st.button("🔄 Refresh Data"):
                    st.rerun()

if __name__ == "__main__":
    main()