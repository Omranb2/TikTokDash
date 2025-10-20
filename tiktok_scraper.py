import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
import math
import urllib.parse
from urllib.parse import quote
import os

class TikTokScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)

    def get_profile_data(self, username):
        """
        Enhanced TikTok profile scraper with advanced regex patterns and comprehensive data extraction
        """
        try:
            # Clean username
            if username.startswith('@'):
                username = username[1:]
            username = username.strip()
            
            # Get comprehensive user information using advanced scraping
            return self._get_user_info_advanced(username)
            
        except Exception as e:
            print(f"Error scraping profile {username}: {str(e)}")
            return None

    def _get_user_info_advanced(self, username):
        """
        Advanced user information extraction with comprehensive patterns
        """
        url = f"https://www.tiktok.com/@{username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = self.session.get(url, headers=headers)

        if response.status_code == 200:
            html_content = response.text
            
            # Try to use lxml parser if available, otherwise use html.parser
            try:
                soup = BeautifulSoup(html_content, 'lxml')
            except:
                soup = BeautifulSoup(html_content, 'html.parser')
            
            # Comprehensive regex patterns for data extraction
            patterns = {
                'user_id': r'"webapp.user-detail":{"userInfo":{"user":{"id":"(\d+)"',
                'unique_id': r'"uniqueId":"(.*?)"',
                'nickname': r'"nickname":"(.*?)"',
                'followers': r'"followerCount":(\d+)',
                'following': r'"followingCount":(\d+)',
                'likes': r'"heartCount":(\d+)|"diggCount":(\d+)|"heart":(\d+)',
                'videos': r'"videoCount":(\d+)',
                'signature': r'"signature":"(.*?)"',
                'verified': r'"verified":(true|false)',
                'secUid': r'"secUid":"(.*?)"',
                'commentSetting': r'"commentSetting":(\d+)',
                'privateAccount': r'"privateAccount":(true|false)',
                'region': r'"ttSeller":false,"region":"([^"]*)"',
                'heart': r'"heart":(\d+)',
                'diggCount': r'"diggCount":(\d+)',
                'friendCount': r'"friendCount":(\d+)',
                'profile_pic': r'"avatarLarger":"(.*?)"'
            }
            
            # Extract information using the defined patterns
            info = {}

            for key, pattern in patterns.items():
                match = re.search(pattern, html_content)
                if match:
                    groups = [g for g in match.groups() if g]  # pick the first non-empty group
                    info[key] = groups[0] if groups else match.group(1)
                else:
                    info[key] = f"No {key} found"

            # Process profile pic URL
            if "profile_pic" in info:
                info['profile_pic'] = info['profile_pic'].replace('\\u002F', '/')
            
            # Extract social links
            social_links = self._extract_social_links(html_content, info.get('signature', ""))
            info['social_links'] = social_links
            
            # Process and calculate metrics
            processed_data = self._process_profile_data(info, username)
            return processed_data
            
        else:
            print(f"Error: Unable to fetch profile. Status code: {response.status_code}")
            return None

    def _extract_social_links(self, html_content, bio):
        """
        Extract social media links from bio and HTML content
        """
        social_links = []
        
        # METHOD 1: Extract links with target parameter
        link_urls = re.findall(r'href="(https://www\.tiktok\.com/link/v2\?[^"]*?scene=bio_url[^"]*?target=([^"&]+))"', html_content)
        for full_url, target in link_urls:
            # Decode the target parameter
            target_decoded = urllib.parse.unquote(target)
            # Look for the text associated with this URL
            text_pattern = rf'href="{re.escape(full_url)}"[^>]*>.*?<span[^>]*SpanLink[^>]*>([^<]+)</span>'
            text_match = re.search(text_pattern, html_content, re.DOTALL)
            if text_match:
                link_text = text_match.group(1)
            else:
                # If we don't find the text, use the target as text
                link_text = target_decoded
                
            # Add to social links if not already present
            if not any(target_decoded in s for s in social_links):
                social_links.append(f"Link: {link_text} - {target_decoded}")
        
        # METHOD 2: Find all SpanLink classes that look like URLs
        span_links = re.findall(r'<span[^>]*class="[^"]*SpanLink[^"]*">([^<]+)</span>', html_content)
        for span_text in span_links:
            # Check if it looks like a URL (contains a dot and no spaces)
            if '.' in span_text and ' ' not in span_text and not any(span_text in s for s in social_links):
                social_links.append(f"Link: {span_text} - {span_text}")
        
        # METHOD 3: Extract Instagram and other social networks mentioned in the bio
        # Instagram
        ig_pattern = re.search(r'[iI][gG]:\s*@?([a-zA-Z0-9._]+)', bio)
        if ig_pattern:
            instagram_username = ig_pattern.group(1)
            if not any(f"Instagram: @{instagram_username}" in s for s in social_links):
                social_links.append(f"Instagram: @{instagram_username}")
        
        # Other social networks in bio
        social_patterns = {
            'snapchat': r'([sS][cC]|[sS]napchat):\s*@?([a-zA-Z0-9._]+)',
            'twitter': r'([tT]witter|[xX]):\s*@?([a-zA-Z0-9._]+)',
            'facebook': r'[fF][bB]:\s*@?([a-zA-Z0-9._]+)',
            'youtube': r'([yY][tT]|[yY]outube):\s*@?([a-zA-Z0-9._]+)',
            'telegram': r'[tT]elegram:\s*@?([a-zA-Z0-9._]+)'
        }
        
        for platform, pattern in social_patterns.items():
            match = re.search(pattern, bio)
            if match:
                username = match.group(2) if len(match.groups()) > 1 else match.group(1)
                social_link = ""
                if platform == 'snapchat':
                    social_link = f"Snapchat: {username}"
                elif platform == 'twitter':
                    social_link = f"Twitter/X: @{username}"
                elif platform == 'facebook':
                    social_link = f"Facebook: {username}"
                elif platform == 'youtube':
                    social_link = f"YouTube: {username}"
                elif platform == 'telegram':
                    social_link = f"Telegram: @{username}"
                
                if social_link and not any(social_link in s for s in social_links):
                    social_links.append(social_link)
        
        # Look for email addresses in the bio
        email_pattern = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', bio)
        if email_pattern:
            email = email_pattern.group(0)
            if not any(email in s for s in social_links):
                social_links.append(f"Email: {email}")
        
        return social_links

    def _process_profile_data(self, info, username):
        """
        Process raw profile data and calculate advanced metrics including influencer score
        """
        try:
            # Parse numeric values safely
            followers = self._parse_count(info.get("followers", "0"))
            likes = self._parse_count(info.get("likes", info.get("heart", "0")))
            videos = max(self._parse_count(info.get("videos", "1")), 1)
            following = self._parse_count(info.get("following", "0"))
            
            # Calculate derived metrics
            avg_likes = likes / videos if videos > 0 else 0
            engagement_rate = (avg_likes / followers) * 100 if followers > 0 else 0
            ff_ratio = followers / following if following > 0 else followers
            
            # NEW INFLUENCER SCORE CALCULATION - Normalized scoring with industry benchmarks
            # Step 1: Normalize metrics to 0-100 scale
            
            # Followers Score (0-100) - Based on follower count
            if followers >= 100_000_000:  # 100M+ followers (top 1%)
                followers_score = 95
            elif followers >= 10_000_000:  # 10M+ followers 
                followers_score = 85
            elif followers >= 1_000_000:   # 1M+ followers
                followers_score = 75
            elif followers >= 100_000:     # 100K+ followers
                followers_score = 60
            elif followers >= 10_000:      # 10K+ followers
                followers_score = 40
            else:
                followers_score = 20
            
            # Engagement Rate Score (0-100) - Based on engagement percentage
            if engagement_rate >= 3:       # 3%+ (high engagement)
                er_score = 90
            elif engagement_rate >= 1:     # 1-3% (average engagement)
                er_score = 50 + ((engagement_rate - 1) / 2) * 40  # Scale 1-3% to 50-90
            else:                          # <1% (low engagement)
                er_score = engagement_rate * 50  # Scale 0-1% to 0-50
            
            # Avg Likes/Video Score (0-100) - Based on average likes
            if avg_likes >= 1_000_000:     # 1M+ likes per video
                likes_score = 85
            elif avg_likes >= 100_000:     # 100K+ likes per video
                likes_score = 70
            elif avg_likes >= 10_000:      # 10K+ likes per video
                likes_score = 55
            elif avg_likes >= 1_000:       # 1K+ likes per video
                likes_score = 40
            else:
                likes_score = 25
            
            # Videos Score (0-100) - Based on content activity
            if videos >= 1000:             # 1000+ videos (very active)
                videos_score = 80
            elif videos >= 500:            # 500+ videos
                videos_score = 70
            elif videos >= 100:            # 100+ videos
                videos_score = 60
            elif videos >= 50:             # 50+ videos
                videos_score = 45
            else:
                videos_score = 30
            
            # Total Likes Score (0-100) - Based on total historical likes
            if likes >= 1_000_000_000:     # 1B+ total likes
                total_likes_score = 90
            elif likes >= 100_000_000:     # 100M+ total likes
                total_likes_score = 80
            elif likes >= 10_000_000:      # 10M+ total likes
                total_likes_score = 70
            elif likes >= 1_000_000:       # 1M+ total likes
                total_likes_score = 55
            else:
                total_likes_score = 35
            
            # Step 2: Apply weights to calculate final influencer score
            influencer_score = round(
                (followers_score * 0.20) +     # Followers: 20%
                (er_score * 0.30) +            # Engagement Rate: 30%
                (likes_score * 0.20) +         # Avg Likes/Video: 20%
                (videos_score * 0.15) +        # Videos: 15%
                (total_likes_score * 0.15),    # Total Likes: 15%
                2
            )
            
            # NEW CREDIBILITY SCORE CALCULATION - Combining Engagement Rate + FF Ratio
            # Step 1: Normalize Engagement Rate (0-100)
            if engagement_rate <= 1:
                er_credibility_score = 50
            elif engagement_rate <= 3:
                # Scale 1-3% to 50-75
                er_credibility_score = 50 + ((engagement_rate - 1) / 2) * 25
            else:
                # 3%+ gets 80-100
                er_credibility_score = min(100, 80 + (engagement_rate - 3) * 5)
            
            # Step 2: Normalize FF Ratio (0-100)
            if ff_ratio >= 10:
                ff_credibility_score = 95
            elif ff_ratio >= 2:
                # Scale 2-10 to 60-95
                ff_credibility_score = 60 + ((ff_ratio - 2) / 8) * 35
            elif ff_ratio >= 1:
                # Scale 1-2 to 40-60
                ff_credibility_score = 40 + ((ff_ratio - 1) / 1) * 20
            else:
                # <1 ratio gets 20-40
                ff_credibility_score = 20 + (ff_ratio * 20)
            
            # Step 3: Calculate combined credibility score (50% each)
            credibility_score = round((er_credibility_score * 0.5) + (ff_credibility_score * 0.5), 2)
            
            # Process verification status
            verified = info.get("verified", "false").lower() == "true" if isinstance(info.get("verified"), str) else bool(info.get("verified", False))
            private_account = info.get("privateAccount", "false").lower() == "true" if isinstance(info.get("privateAccount"), str) else bool(info.get("privateAccount", False))
            
            # Return processed data in consistent format
            return {
                'username': info.get('unique_id', username),
                'display_name': info.get('nickname', ''),
                'bio': info.get('signature', ''),
                'follower_count': followers,
                'following_count': following,
                'heart_count': likes,
                'video_count': videos,
                'verified': verified,
                'private_account': private_account,
                'avatar_url': info.get('profile_pic', ''),
                'social_links': info.get('social_links', []),
                
                # Advanced metrics with new scoring
                'avg_likes_per_video': round(avg_likes, 2),
                'engagement_rate': round(engagement_rate, 2),
                'follower_following_ratio': round(ff_ratio, 2),
                'influencer_score': influencer_score,
                'credibility_score': credibility_score,
                'authenticity_score': influencer_score,  # Same value unless computed differently
                'verified_verdict': "Yes" if verified else "No",
                'private_account_verdict': "Yes" if private_account else "No"
            }
            
        except Exception as e:
            print(f"Error processing profile data: {str(e)}")
            return None

    def _parse_count(self, count_str):
        """
        Parse count strings like '1.2M', '5K', '100' to integers
        """
        if not count_str:
            return 0
        
        try:
            count_str = str(count_str).lower().replace(',', '').strip()
            
            if 'b' in count_str:
                return int(float(count_str.replace('b', '')) * 1_000_000_000)
            elif 'm' in count_str:
                return int(float(count_str.replace('m', '')) * 1_000_000)
            elif 'k' in count_str:
                return int(float(count_str.replace('k', '')) * 1_000)
            else:
                return int(float(count_str))
                
        except:
            return 0

    def get_recent_videos(self, username, limit=10):
        """
        Get recent videos for a user (if available)
        """
        try:
            # This would require additional API calls or more complex scraping
            # For now, return empty list as video scraping is more complex and rate-limited
            return []
            
        except Exception as e:
            print(f"Error getting recent videos: {str(e)}")
            return []
