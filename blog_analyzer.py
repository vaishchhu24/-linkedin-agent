#!/usr/bin/env python3
"""
Blog Analyzer - Crawls and analyzes the client's blog to understand their authentic voice and style.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin, urlparse
import time
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class BlogAnalyzer:
    def __init__(self, base_url):
        """
        Initialize the blog analyzer.
        
        Args:
            base_url: The main URL of the client's blog
        """
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls = set()
        self.blog_posts = []
        self.analysis = {}
        
    def crawl_blog(self, max_posts=20):
        """
        Crawl the blog to find and extract blog posts.
        
        Args:
            max_posts: Maximum number of blog posts to analyze
        """
        print(f"🔍 Crawling blog: {self.base_url}")
        print(f"📊 Target: {max_posts} blog posts")
        
        try:
            # Start with the main page
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find blog post links
            post_links = self.find_blog_post_links(soup)
            
            print(f"📝 Found {len(post_links)} potential blog post links")
            
            # Extract content from each blog post
            for i, link in enumerate(post_links[:max_posts]):
                print(f"📖 Analyzing post {i+1}/{min(len(post_links), max_posts)}: {link}")
                
                try:
                    post_content = self.extract_blog_post(link)
                    if post_content:
                        self.blog_posts.append(post_content)
                        time.sleep(1)  # Be respectful to the server
                except Exception as e:
                    print(f"❌ Error extracting post {link}: {e}")
                    continue
            
            print(f"✅ Successfully analyzed {len(self.blog_posts)} blog posts")
            
        except Exception as e:
            print(f"❌ Error crawling blog: {e}")
    
    def find_blog_post_links(self, soup):
        """
        Find links to blog posts on the main page.
        """
        links = []
        
        # Common patterns for blog post links
        selectors = [
            'a[href*="/blog/"]',
            'a[href*="/post/"]',
            'a[href*="/article/"]',
            'a[href*="/news/"]',
            'article a',
            '.blog-post a',
            '.post-link',
            '.article-link'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    if self.is_valid_blog_url(full_url):
                        links.append(full_url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links
    
    def is_valid_blog_url(self, url):
        """
        Check if URL is a valid blog post URL.
        """
        if url in self.visited_urls:
            return False
        
        parsed = urlparse(url)
        if parsed.netloc != self.domain:
            return False
        
        # Skip common non-blog pages
        skip_patterns = [
            '/tag/', '/category/', '/author/', '/page/',
            '/about/', '/contact/', '/privacy/', '/terms/',
            '/search', '/sitemap', '/feed', '/rss'
        ]
        
        for pattern in skip_patterns:
            if pattern in url:
                return False
        
        return True
    
    def extract_blog_post(self, url):
        """
        Extract content from a single blog post.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self.extract_title(soup)
            
            # Extract content
            content = self.extract_content(soup)
            
            # Extract metadata
            metadata = self.extract_metadata(soup, url)
            
            if title and content:
                return {
                    'url': url,
                    'title': title,
                    'content': content,
                    'metadata': metadata
                }
            
        except Exception as e:
            print(f"❌ Error extracting post from {url}: {e}")
        
        return None
    
    def extract_title(self, soup):
        """
        Extract the blog post title.
        """
        # Common title selectors
        title_selectors = [
            'h1',
            '.post-title',
            '.article-title',
            '.entry-title',
            'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 10:
                    return title
        
        return None
    
    def extract_content(self, soup):
        """
        Extract the main content of the blog post.
        """
        # Common content selectors
        content_selectors = [
            '.post-content',
            '.article-content',
            '.entry-content',
            '.blog-content',
            'article',
            '.content',
            'main'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # Remove unwanted elements
                for unwanted in element.select('script, style, nav, header, footer, .sidebar, .comments'):
                    unwanted.decompose()
                
                content = element.get_text()
                content = self.clean_text(content)
                
                if content and len(content) > 100:
                    return content
        
        return None
    
    def extract_metadata(self, soup, url):
        """
        Extract metadata from the blog post.
        """
        metadata = {
            'url': url,
            'date': None,
            'author': None,
            'tags': [],
            'categories': []
        }
        
        # Extract date
        date_selectors = [
            '.post-date',
            '.article-date',
            '.entry-date',
            'time',
            '.date'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_text = element.get_text().strip()
                if date_text:
                    metadata['date'] = date_text
                    break
        
        # Extract author
        author_selectors = [
            '.post-author',
            '.article-author',
            '.entry-author',
            '.author'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                author_text = element.get_text().strip()
                if author_text:
                    metadata['author'] = author_text
                    break
        
        return metadata
    
    def clean_text(self, text):
        """
        Clean and normalize text content.
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text.strip()
    
    def analyze_writing_style(self):
        """
        Analyze the writing style and patterns in the blog posts.
        """
        print("📊 Analyzing writing style...")
        
        if not self.blog_posts:
            print("❌ No blog posts to analyze")
            return
        
        all_text = ' '.join([post['content'] for post in self.blog_posts])
        
        # Basic statistics
        words = word_tokenize(all_text.lower())
        sentences = sent_tokenize(all_text)
        
        # Remove stopwords for analysis
        stop_words = set(stopwords.words('english'))
        content_words = [word for word in words if word.isalpha() and word not in stop_words]
        
        # Analyze sentence length
        sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
        
        # Analyze word frequency
        word_freq = Counter(content_words)
        
        # Analyze paragraph structure
        paragraphs = [post['content'].split('\n\n') for post in self.blog_posts]
        paragraph_lengths = []
        for para_list in paragraphs:
            for para in para_list:
                if para.strip():
                    para_words = len(word_tokenize(para))
                    paragraph_lengths.append(para_words)
        
        # Common phrases and patterns
        phrases = self.extract_common_phrases(all_text)
        
        # Tone analysis
        tone_indicators = self.analyze_tone(all_text)
        
        self.analysis = {
            'total_posts': len(self.blog_posts),
            'total_words': len(words),
            'total_sentences': len(sentences),
            'avg_sentence_length': sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            'avg_paragraph_length': sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0,
            'most_common_words': word_freq.most_common(20),
            'common_phrases': phrases,
            'tone_indicators': tone_indicators,
            'writing_patterns': self.identify_writing_patterns(),
            'topics': self.identify_topics()
        }
        
        print("✅ Writing style analysis complete")
    
    def extract_common_phrases(self, text):
        """
        Extract common phrases and expressions.
        """
        # Look for common HR consulting phrases
        hr_phrases = [
            'hr consultant', 'human resources', 'employee', 'workplace',
            'business owner', 'entrepreneur', 'corporate', 'consulting',
            'client', 'pricing', 'value', 'struggle', 'challenge',
            'success', 'growth', 'learning', 'experience'
        ]
        
        phrases = {}
        for phrase in hr_phrases:
            count = text.lower().count(phrase)
            if count > 0:
                phrases[phrase] = count
        
        return phrases
    
    def analyze_tone(self, text):
        """
        Analyze the tone of the writing.
        """
        tone_indicators = {
            'personal': 0,
            'professional': 0,
            'conversational': 0,
            'formal': 0,
            'encouraging': 0,
            'vulnerable': 0
        }
        
        # Personal tone indicators
        personal_words = ['i', 'me', 'my', 'mine', 'myself', 'i\'ve', 'i\'m', 'i\'ll']
        for word in personal_words:
            tone_indicators['personal'] += text.lower().count(word)
        
        # Conversational tone indicators
        conversational_words = ['you', 'your', 'you\'re', 'you\'ve', 'you\'ll', 'let\'s', 'we', 'us']
        for word in conversational_words:
            tone_indicators['conversational'] += text.lower().count(word)
        
        # Encouraging tone indicators
        encouraging_words = ['can', 'will', 'success', 'growth', 'help', 'support', 'achieve', 'reach']
        for word in encouraging_words:
            tone_indicators['encouraging'] += text.lower().count(word)
        
        # Vulnerable tone indicators
        vulnerable_words = ['struggle', 'difficult', 'challenge', 'hard', 'scared', 'nervous', 'worried', 'doubt']
        for word in vulnerable_words:
            tone_indicators['vulnerable'] += text.lower().count(word)
        
        return tone_indicators
    
    def identify_writing_patterns(self):
        """
        Identify common writing patterns and structures.
        """
        patterns = {
            'storytelling': 0,
            'question_asking': 0,
            'list_format': 0,
            'personal_experience': 0,
            'advice_giving': 0
        }
        
        for post in self.blog_posts:
            content = post['content'].lower()
            
            # Storytelling patterns
            if any(word in content for word in ['remember', 'when i', 'story', 'experience']):
                patterns['storytelling'] += 1
            
            # Question asking patterns
            if '?' in content:
                patterns['question_asking'] += 1
            
            # List format patterns
            if any(char in content for char in ['•', '-', '1.', '2.', '3.']):
                patterns['list_format'] += 1
            
            # Personal experience patterns
            if any(word in content for word in ['i learned', 'i found', 'i discovered', 'i realized']):
                patterns['personal_experience'] += 1
            
            # Advice giving patterns
            if any(word in content for word in ['should', 'need to', 'must', 'important to']):
                patterns['advice_giving'] += 1
        
        return patterns
    
    def identify_topics(self):
        """
        Identify common topics and themes.
        """
        topics = {
            'pricing': 0,
            'client_acquisition': 0,
            'business_growth': 0,
            'imposter_syndrome': 0,
            'work_life_balance': 0,
            'networking': 0,
            'value_proposition': 0
        }
        
        topic_keywords = {
            'pricing': ['price', 'charge', 'cost', 'value', 'hourly', 'package'],
            'client_acquisition': ['client', 'prospect', 'lead', 'sales', 'pitch'],
            'business_growth': ['grow', 'scale', 'expand', 'success', 'revenue'],
            'imposter_syndrome': ['imposter', 'doubt', 'confidence', 'worthy', 'deserve'],
            'work_life_balance': ['balance', 'time', 'family', 'personal', 'life'],
            'networking': ['network', 'connect', 'relationship', 'referral'],
            'value_proposition': ['value', 'benefit', 'outcome', 'result', 'impact']
        }
        
        for post in self.blog_posts:
            content = post['content'].lower()
            
            for topic, keywords in topic_keywords.items():
                if any(keyword in content for keyword in keywords):
                    topics[topic] += 1
        
        return topics
    
    def save_analysis(self, filename='blog_analysis.json'):
        """
        Save the analysis results to a JSON file.
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.analysis, f, indent=2)
            print(f"✅ Analysis saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving analysis: {e}")
    
    def generate_style_guide(self):
        """
        Generate a style guide based on the analysis.
        """
        if not self.analysis:
            print("❌ No analysis available. Run analyze_writing_style() first.")
            return
        
        style_guide = {
            'voice_and_tone': {
                'primary_tone': 'personal' if self.analysis['tone_indicators']['personal'] > self.analysis['tone_indicators']['professional'] else 'professional',
                'conversational_level': 'high' if self.analysis['tone_indicators']['conversational'] > 10 else 'moderate',
                'vulnerability_level': 'high' if self.analysis['tone_indicators']['vulnerable'] > 5 else 'moderate'
            },
            'writing_structure': {
                'avg_sentence_length': round(self.analysis['avg_sentence_length'], 1),
                'avg_paragraph_length': round(self.analysis['avg_paragraph_length'], 1),
                'preferred_formats': [k for k, v in self.analysis['writing_patterns'].items() if v > 0]
            },
            'common_topics': [k for k, v in self.analysis['topics'].items() if v > 0],
            'frequently_used_words': [word for word, count in self.analysis['most_common_words'][:10]],
            'common_phrases': list(self.analysis['common_phrases'].keys())
        }
        
        return style_guide

def main():
    """
    Main function to run the blog analyzer.
    """
    print("📊 Blog Analyzer for LinkedIn Post Generation")
    print("=" * 50)
    
    # Get the blog URL from user
    blog_url = input("Enter the blog URL: ").strip()
    
    if not blog_url:
        print("❌ No URL provided")
        return
    
    # Initialize analyzer
    analyzer = BlogAnalyzer(blog_url)
    
    # Crawl the blog
    analyzer.crawl_blog(max_posts=15)
    
    if analyzer.blog_posts:
        # Analyze writing style
        analyzer.analyze_writing_style()
        
        # Save analysis
        analyzer.save_analysis()
        
        # Generate style guide
        style_guide = analyzer.generate_style_guide()
        
        print("\n📋 Style Guide Generated:")
        print("=" * 30)
        print(f"Voice & Tone: {style_guide['voice_and_tone']['primary_tone']}")
        print(f"Conversational: {style_guide['voice_and_tone']['conversational_level']}")
        print(f"Vulnerability: {style_guide['voice_and_tone']['vulnerability_level']}")
        print(f"Avg Sentence Length: {style_guide['writing_structure']['avg_sentence_length']} words")
        print(f"Avg Paragraph Length: {style_guide['writing_structure']['avg_paragraph_length']} words")
        print(f"Common Topics: {', '.join(style_guide['common_topics'])}")
        print(f"Frequent Words: {', '.join(style_guide['frequently_used_words'][:5])}")
        
        print("\n✅ Blog analysis complete! Use this data to improve LinkedIn post generation.")
    else:
        print("❌ No blog posts found to analyze")

if __name__ == "__main__":
    main() 