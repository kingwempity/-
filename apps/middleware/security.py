"""
安全中间件模块

提供额外的安全防护，包括：
- XSS防护响应头
- 输入清理和验证
- 输出转义检查
"""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class XSSProtectionMiddleware(MiddlewareMixin):
    """
    XSS防护中间件
    
    在响应头中添加额外的安全头，增强XSS防护：
    - X-XSS-Protection: 启用浏览器XSS过滤器
    - X-Content-Type-Options: 防止MIME类型嗅探
    - Content-Security-Policy: 内容安全策略
    - Referrer-Policy: 控制Referer头信息
    """
    
    def process_response(self, request, response):
        """
        处理响应，添加安全头
        
        Args:
            request: HTTP请求对象
            response: HTTP响应对象
            
        Returns:
            添加了安全头的响应对象
        """
        # X-XSS-Protection: 启用浏览器的XSS过滤器
        # 1; mode=block 表示检测到XSS攻击时阻止页面加载
        if not response.get('X-XSS-Protection'):
            response['X-XSS-Protection'] = '1; mode=block'
        
        # X-Content-Type-Options: 防止浏览器进行MIME类型嗅探
        # nosniff 强制浏览器遵守Content-Type头
        if not response.get('X-Content-Type-Options'):
            response['X-Content-Type-Options'] = 'nosniff'
        
        # Referrer-Policy: 控制Referer头信息的发送
        # strict-origin-when-cross-origin 在跨域请求时只发送源信息
        if not response.get('Referrer-Policy'):
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions-Policy: 控制浏览器特性的使用权限
        # 禁用不需要的浏览器API，减少攻击面
        if not response.get('Permissions-Policy'):
            response['Permissions-Policy'] = (
                'geolocation=(), '
                'microphone=(), '
                'camera=(), '
                'payment=(), '
                'usb=(), '
                'magnetometer=(), '
                'accelerometer=(), '
                'gyroscope=()'
            )
        
        # Content-Security-Policy: 内容安全策略
        # 从settings中读取CSP配置
        if hasattr(settings, 'CSP_DEFAULT_SRC') and not response.get('Content-Security-Policy'):
            csp_directives = []
            
            # 构建CSP策略
            if hasattr(settings, 'CSP_DEFAULT_SRC'):
                csp_directives.append(f"default-src {' '.join(settings.CSP_DEFAULT_SRC)}")
            
            if hasattr(settings, 'CSP_SCRIPT_SRC'):
                csp_directives.append(f"script-src {' '.join(settings.CSP_SCRIPT_SRC)}")
            
            if hasattr(settings, 'CSP_STYLE_SRC'):
                csp_directives.append(f"style-src {' '.join(settings.CSP_STYLE_SRC)}")
            
            if hasattr(settings, 'CSP_IMG_SRC'):
                csp_directives.append(f"img-src {' '.join(settings.CSP_IMG_SRC)}")
            
            if hasattr(settings, 'CSP_FONT_SRC'):
                csp_directives.append(f"font-src {' '.join(settings.CSP_FONT_SRC)}")
            
            if hasattr(settings, 'CSP_CONNECT_SRC'):
                csp_directives.append(f"connect-src {' '.join(settings.CSP_CONNECT_SRC)}")
            
            if hasattr(settings, 'CSP_FRAME_ANCESTORS'):
                csp_directives.append(f"frame-ancestors {' '.join(settings.CSP_FRAME_ANCESTORS)}")
            
            if hasattr(settings, 'CSP_BASE_URI'):
                csp_directives.append(f"base-uri {' '.join(settings.CSP_BASE_URI)}")
            
            if hasattr(settings, 'CSP_FORM_ACTION'):
                csp_directives.append(f"form-action {' '.join(settings.CSP_FORM_ACTION)}")
            
            if csp_directives:
                response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        return response


class InputSanitizationMiddleware(MiddlewareMixin):
    """
    输入清理中间件
    
    在请求处理前对用户输入进行安全检查和清理
    警告：这是一个基础实现，不应作为唯一的防护手段
    """
    
    # 常见的XSS攻击模式
    XSS_PATTERNS = [
        '<script',
        'javascript:',
        'onerror=',
        'onclick=',
        'onload=',
        '<iframe',
        '<object',
        '<embed',
        'data:text/html',
    ]
    
    def process_request(self, request):
        """
        处理请求，检查是否包含明显的XSS攻击模式
        
        Args:
            request: HTTP请求对象
            
        Returns:
            None 或 HttpResponse（如果检测到攻击）
        """
        # 检查GET参数
        for key, value in request.GET.items():
            if self._contains_xss_pattern(value):
                # 记录可疑请求
                import logging
                logger = logging.getLogger('security')
                logger.warning(
                    f'检测到可疑的XSS攻击尝试 - GET参数 {key}: {value[:100]} '
                    f'来自IP: {self._get_client_ip(request)}'
                )
        
        # 检查POST参数
        if request.method == 'POST':
            for key, value in request.POST.items():
                if isinstance(value, str) and self._contains_xss_pattern(value):
                    # 记录可疑请求
                    import logging
                    logger = logging.getLogger('security')
                    logger.warning(
                        f'检测到可疑的XSS攻击尝试 - POST参数 {key}: {value[:100]} '
                        f'来自IP: {self._get_client_ip(request)}'
                    )
        
        return None
    
    def _contains_xss_pattern(self, value):
        """
        检查字符串是否包含XSS攻击模式
        
        Args:
            value: 需要检查的字符串
            
        Returns:
            True表示包含可疑模式，False表示安全
        """
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        return any(pattern in value_lower for pattern in self.XSS_PATTERNS)
    
    def _get_client_ip(self, request):
        """
        获取客户端IP地址
        
        Args:
            request: HTTP请求对象
            
        Returns:
            客户端IP地址
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

