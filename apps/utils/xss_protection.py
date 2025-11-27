"""
XSS攻击防护工具模块

提供XSS攻击防护相关的工具函数，包括：
- HTML转义：防止恶意脚本注入
- 输入过滤：清理危险的HTML标签和属性
- URL验证：防止JavaScript伪协议注入

使用说明：
1. 对于所有用户输入，在存储前使用clean_input()进行过滤
2. 对于需要允许部分HTML的场景，使用sanitize_html()
3. 对于输出到HTML的数据，Django模板会自动转义，但JavaScript中需要手动使用escape_html()
"""

import re
import html
from typing import Optional
from django.utils.html import escape, strip_tags


def escape_html(text: str) -> str:
    """
    HTML转义函数
    
    将HTML特殊字符转义为实体，防止XSS攻击
    
    Args:
        text: 需要转义的文本
        
    Returns:
        转义后的安全文本
        
    Example:
        >>> escape_html('<script>alert("XSS")</script>')
        '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'
    """
    if not text:
        return ""
    return html.escape(str(text), quote=True)


def clean_input(text: str, max_length: Optional[int] = None) -> str:
    """
    清理用户输入，移除所有HTML标签和潜在的危险字符
    
    用于普通文本输入字段（如书名、作者、用户名等）
    
    Args:
        text: 用户输入的文本
        max_length: 最大长度限制，超过将被截断
        
    Returns:
        清理后的安全文本
        
    Example:
        >>> clean_input('<script>alert("XSS")</script>Book Title')
        'alert("XSS")Book Title'
    """
    if not text:
        return ""
    
    # 移除所有HTML标签
    cleaned = strip_tags(str(text))
    
    # 移除常见的XSS危险字符序列
    dangerous_patterns = [
        r'javascript:',
        r'on\w+\s*=',  # 事件处理器 (onclick=, onerror=, etc.)
        r'<\s*script',
        r'<\s*iframe',
        r'<\s*object',
        r'<\s*embed',
        r'<\s*link',
        r'<\s*style',
        r'expression\s*\(',  # CSS expression
    ]
    
    for pattern in dangerous_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # 限制长度
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned.strip()


def sanitize_html(text: str, allowed_tags: Optional[list] = None) -> str:
    """
    清理HTML内容，只保留安全的标签和属性
    
    用于允许部分HTML格式的场景（如富文本编辑器）
    
    Args:
        text: 包含HTML的文本
        allowed_tags: 允许的HTML标签列表，默认为['p', 'br', 'strong', 'em', 'u']
        
    Returns:
        清理后的安全HTML
        
    Note:
        这是一个基础实现，对于复杂的富文本场景，建议使用专业库如bleach
    """
    if not text:
        return ""
    
    if allowed_tags is None:
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'b', 'i']
    
    # 对于简单场景，直接移除所有标签
    # 如需支持富文本，建议使用bleach库
    return strip_tags(str(text))


def validate_url(url: str) -> bool:
    """
    验证URL是否安全，防止JavaScript伪协议注入
    
    Args:
        url: 需要验证的URL
        
    Returns:
        True表示安全，False表示不安全
        
    Example:
        >>> validate_url('http://example.com')
        True
        >>> validate_url('javascript:alert(1)')
        False
    """
    if not url:
        return False
    
    # 移除空白字符
    url = url.strip().lower()
    
    # 检查危险的协议
    dangerous_protocols = [
        'javascript:',
        'data:',
        'vbscript:',
        'file:',
    ]
    
    for protocol in dangerous_protocols:
        if url.startswith(protocol):
            return False
    
    # 只允许http, https, mailto, tel等安全协议
    safe_protocols = ['http://', 'https://', 'mailto:', 'tel:', '/', '#']
    
    return any(url.startswith(protocol) for protocol in safe_protocols)


def escape_js_string(text: str) -> str:
    """
    转义JavaScript字符串，防止在JS上下文中的XSS攻击
    
    Args:
        text: 需要转义的文本
        
    Returns:
        转义后的安全文本
        
    Example:
        >>> escape_js_string('Hello "World"')
        'Hello \\"World\\"'
    """
    if not text:
        return ""
    
    # 转义特殊字符
    text = str(text)
    text = text.replace('\\', '\\\\')  # 反斜杠
    text = text.replace('"', '\\"')    # 双引号
    text = text.replace("'", "\\'")    # 单引号
    text = text.replace('\n', '\\n')   # 换行符
    text = text.replace('\r', '\\r')   # 回车符
    text = text.replace('\t', '\\t')   # 制表符
    text = text.replace('</', '<\\/')  # 闭合script标签
    
    return text


def is_safe_content(text: str) -> tuple[bool, Optional[str]]:
    """
    检查文本内容是否包含潜在的XSS攻击代码
    
    Args:
        text: 需要检查的文本
        
    Returns:
        (是否安全, 不安全的原因)
        
    Example:
        >>> is_safe_content('Normal text')
        (True, None)
        >>> is_safe_content('<script>alert(1)</script>')
        (False, '包含script标签')
    """
    if not text:
        return True, None
    
    text_lower = str(text).lower()
    
    # 检测危险的标签
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'link', 'style']
    for tag in dangerous_tags:
        if f'<{tag}' in text_lower:
            return False, f'包含{tag}标签'
    
    # 检测事件处理器
    event_handlers = ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus', 'onblur']
    for event in event_handlers:
        if event in text_lower:
            return False, f'包含事件处理器{event}'
    
    # 检测JavaScript伪协议
    if 'javascript:' in text_lower:
        return False, '包含JavaScript伪协议'
    
    # 检测data URI
    if 'data:text/html' in text_lower or 'data:image/svg+xml' in text_lower:
        return False, '包含危险的data URI'
    
    return True, None

