"""
XSS防护工具测试模块

测试XSS防护相关的工具函数，确保防护机制正常工作
"""

from django.test import TestCase
from apps.utils.xss_protection import (
    escape_html,
    clean_input,
    sanitize_html,
    validate_url,
    escape_js_string,
    is_safe_content
)


class XSSProtectionTests(TestCase):
    """XSS防护工具测试类"""
    
    def test_escape_html_basic(self):
        """测试HTML转义 - 基本功能"""
        # 测试常见的HTML特殊字符
        result = escape_html('<script>alert("XSS")</script>')
        self.assertEqual(result, '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;')
        
        result = escape_html('<img src=x onerror=alert(1)>')
        self.assertIn('&lt;', result)
        self.assertIn('&gt;', result)
        self.assertNotIn('<', result)
        self.assertNotIn('>', result)
    
    def test_escape_html_special_chars(self):
        """测试HTML转义 - 特殊字符"""
        result = escape_html('&<>"\'')
        self.assertIn('&amp;', result)
        self.assertIn('&lt;', result)
        self.assertIn('&gt;', result)
        self.assertIn('&quot;', result)
        self.assertIn('&#x27;', result)
    
    def test_escape_html_empty(self):
        """测试HTML转义 - 空值处理"""
        self.assertEqual(escape_html(''), '')
        self.assertEqual(escape_html(None), '')
    
    def test_clean_input_basic(self):
        """测试输入清理 - 基本功能"""
        result = clean_input('<script>alert(1)</script>Book Title')
        self.assertNotIn('<script>', result)
        self.assertNotIn('</script>', result)
        self.assertIn('Book Title', result)
    
    def test_clean_input_dangerous_patterns(self):
        """测试输入清理 - 危险模式"""
        test_cases = [
            ('javascript:alert(1)', ''),
            ('onclick=alert(1)', ''),
            ('<iframe src="evil.com"></iframe>', ''),
            ('onerror=alert(1)', ''),
        ]
        
        for input_text, expected_substring in test_cases:
            result = clean_input(input_text)
            self.assertNotIn('javascript:', result.lower())
            self.assertNotIn('onclick', result.lower())
            self.assertNotIn('onerror', result.lower())
            self.assertNotIn('<iframe', result.lower())
    
    def test_clean_input_length_limit(self):
        """测试输入清理 - 长度限制"""
        long_text = 'A' * 1000
        result = clean_input(long_text, max_length=100)
        self.assertEqual(len(result), 100)
    
    def test_sanitize_html(self):
        """测试HTML清理"""
        result = sanitize_html('<p>Hello <script>alert(1)</script></p>')
        self.assertNotIn('<script>', result)
        self.assertNotIn('</script>', result)
    
    def test_validate_url_safe(self):
        """测试URL验证 - 安全URL"""
        safe_urls = [
            'http://example.com',
            'https://example.com',
            'mailto:test@example.com',
            'tel:1234567890',
            '/relative/path',
            '#anchor',
        ]
        
        for url in safe_urls:
            self.assertTrue(validate_url(url), f'URL应该是安全的: {url}')
    
    def test_validate_url_dangerous(self):
        """测试URL验证 - 危险URL"""
        dangerous_urls = [
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
            'vbscript:msgbox(1)',
            'file:///etc/passwd',
        ]
        
        for url in dangerous_urls:
            self.assertFalse(validate_url(url), f'URL应该被标记为危险: {url}')
    
    def test_escape_js_string(self):
        """测试JavaScript字符串转义"""
        result = escape_js_string('Hello "World"')
        self.assertEqual(result, 'Hello \\"World\\"')
        
        result = escape_js_string("It's a test")
        self.assertEqual(result, "It\\'s a test")
        
        result = escape_js_string('Line1\nLine2')
        self.assertEqual(result, 'Line1\\nLine2')
    
    def test_is_safe_content_safe(self):
        """测试内容安全检查 - 安全内容"""
        safe_contents = [
            'Normal text',
            'Book Title: Python Programming',
            'Author: John Doe',
            'Email: test@example.com',
        ]
        
        for content in safe_contents:
            is_safe, reason = is_safe_content(content)
            self.assertTrue(is_safe, f'内容应该是安全的: {content}')
            self.assertIsNone(reason)
    
    def test_is_safe_content_dangerous(self):
        """测试内容安全检查 - 危险内容"""
        dangerous_contents = [
            ('<script>alert(1)</script>', 'script标签'),
            ('<iframe src="evil.com"></iframe>', 'iframe标签'),
            ('onclick=alert(1)', '事件处理器'),
            ('javascript:alert(1)', 'JavaScript伪协议'),
            ('data:text/html,<script>alert(1)</script>', 'data URI'),
        ]
        
        for content, expected_keyword in dangerous_contents:
            is_safe, reason = is_safe_content(content)
            self.assertFalse(is_safe, f'内容应该被标记为危险: {content}')
            self.assertIsNotNone(reason)
            self.assertIn('包含', reason)


class XSSAttackSimulationTests(TestCase):
    """XSS攻击模拟测试类"""
    
    def test_reflected_xss_attack(self):
        """测试反射型XSS攻击防护"""
        # 模拟通过URL参数注入恶意脚本
        from django.test import Client
        client = Client()
        
        # 尝试在图书查询中注入脚本
        xss_payloads = [
            '<script>alert(1)</script>',
            '<img src=x onerror=alert(1)>',
            '<svg onload=alert(1)>',
            'javascript:alert(1)',
        ]
        
        for payload in xss_payloads:
            response = client.get('/library/', {'q': payload})
            # 检查响应中是否包含未转义的脚本
            content = response.content.decode('utf-8')
            self.assertNotIn('<script>', content.lower())
            self.assertNotIn('onerror=', content.lower())
            self.assertNotIn('onload=', content.lower())
            self.assertNotIn('javascript:', content.lower())
    
    def test_stored_xss_prevention(self):
        """测试存储型XSS防护"""
        from apps.library.models import Book
        from apps.utils.xss_protection import clean_input
        
        # 尝试创建包含恶意脚本的图书
        malicious_title = '<script>alert("XSS")</script>Test Book'
        cleaned_title = clean_input(malicious_title)
        
        # 验证标题已被清理
        self.assertNotIn('<script>', cleaned_title)
        self.assertNotIn('</script>', cleaned_title)
        
        # 创建图书
        book = Book.objects.create(
            title=cleaned_title,
            author='Test Author',
            isbn='9780000000001',
            publisher='Test Publisher',
            category='Test',
            total_copies=1,
            available_copies=1
        )
        
        # 验证从数据库读取的数据也是安全的
        retrieved_book = Book.objects.get(id=book.id)
        self.assertNotIn('<script>', retrieved_book.title)
    
    def test_dom_xss_prevention(self):
        """测试DOM型XSS防护"""
        # 验证JavaScript中的动态内容插入是否安全
        from django.test import Client
        client = Client()
        
        # 访问Dashboard页面（包含大量JavaScript动态内容）
        # 注意：需要先登录管理员账户
        from apps.accounts.models import User
        admin_user = User.objects.create_user(
            username='testadmin',
            password='testpass123',
            role='admin'
        )
        client.force_login(admin_user)
        
        response = client.get('/')
        content = response.content.decode('utf-8')
        
        # 检查页面是否包含XSS防护函数
        self.assertIn('escapeHtml', content)
        
        # 清理测试数据
        admin_user.delete()


class SecurityMiddlewareTests(TestCase):
    """安全中间件测试类"""
    
    def test_xss_protection_headers(self):
        """测试XSS防护响应头"""
        from django.test import Client
        client = Client()
        
        response = client.get('/')
        
        # 检查XSS防护头是否存在
        self.assertIn('X-XSS-Protection', response)
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
        
        # 检查Content-Type保护头
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        
        # 检查Referrer-Policy头
        self.assertIn('Referrer-Policy', response)
    
    def test_csp_header(self):
        """测试内容安全策略(CSP)头"""
        from django.test import Client
        client = Client()
        
        response = client.get('/')
        
        # 检查CSP头是否存在
        self.assertIn('Content-Security-Policy', response)
        
        csp = response['Content-Security-Policy']
        # 验证CSP包含必要的指令
        self.assertIn('default-src', csp)
        self.assertIn('script-src', csp)
        self.assertIn('style-src', csp)

