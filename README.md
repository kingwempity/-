# 校园图书借阅管理系统

一个基于Django和MySQL的高性能、安全可靠的校园图书借阅管理系统，支持图书管理、借阅归还、数据统计与可视化等功能。

## 项目概述

本系统采用Django作为Web框架，MySQL作为数据库，实现了完整的图书借阅管理业务流程，包括：

- **图书管理**：图书信息录入、查询、修改、删除、批量导入
- **借阅管理**：借阅登记、归还、续借、逾期处理
- **用户管理**：基于RBAC的权限控制，支持管理员、图书管理员、学生三种角色
- **数据统计**：系统运营数据的统计分析和可视化展示（Dashboard模块）

## 技术栈

- **后端框架**：Django 5.0.1
- **数据库**：MySQL（使用InnoDB存储引擎，支持事务）
- **前端**：TailwindCSS + Chart.js（数据可视化）
- **认证方式**：基于Django Session的Cookie认证
- **权限控制**：RBAC（基于角色的访问控制）

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+ 或 8.0+
- pip

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd Process
```

2. **安装依赖**
```bash
pip install django mysqlclient
# 或使用 requirements.txt
pip install -r requirements.txt
```

3. **配置数据库**

编辑 `core/settings.py`，修改数据库配置：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'book',
        'USER': 'book',
        'PASSWORD': 'book',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

4. **初始化数据库**
```bash
python manage.py migrate
```

5. **创建超级管理员**
```bash
python manage.py createsuperuser
```

6. **启动开发服务器**
```bash
python manage.py runserver 0.0.0.0:8000
```

访问 http://127.0.0.1:8000/ 即可使用系统。

### 默认账户

- **超级管理员**
  - 用户名：SuperAdmin
  - 密码：Admin@5521

- **学生测试账户**
  - 用户名：TC-A-001
  - 密码：TEST@001

## 功能模块

### 1. 图书管理模块（library）

**功能**：
- 图书信息录入（书名、作者、ISBN、出版社、分类、馆藏数量等）
- 多维度模糊查询（书名、作者、ISBN、分类）
- 图书信息修改和删除
- 批量导入（支持CSV/Excel格式）

**权限**：
- 查询：所有已登录用户
- 增删改：管理员、图书管理员

**API接口**：
- `GET /library/` - 图书查询页面
- `GET /api/books` - 图书查询API（JSON）
- `POST /api/books` - 创建图书
- `GET /api/books/{id}` - 图书详情
- `PUT /api/books/{id}` - 更新图书
- `DELETE /api/books/{id}` - 删除图书
- `POST /api/books/import` - 批量导入

### 2. 借阅管理模块（borrowing）

**功能**：
- 借阅登记（自动检查库存、用户状态，支持 15/30/45/60 天的借阅时长选择，最长 60 天）
- 图书归还（自动计算逾期和罚款）
- 续借功能（限制续借次数，单次续借新增时长 ≤ 30 天）
- 借阅记录查询（个人/全部）
- 逾期标记与罚款计算

**权限**：
- 借阅/归还/续借：学生、管理员、图书管理员
- 查询全部记录：管理员、图书管理员

**API接口**：
- `POST /api/borrow` - 借阅登记
- `POST /api/return` - 归还图书
- `POST /api/renew` - 续借
- `GET /api/borrows` - 个人借阅记录
- `GET /api/borrows/all` - 全部借阅记录（管理员）
- `GET /api/rule` - 查询罚款规则
- `PUT /api/rule` - 更新罚款规则（管理员）

**管理命令**：
```bash
python manage.py mark_overdue  # 标记逾期记录
```

### 3. 用户管理模块（accounts）

**功能**：
- 用户注册与登录
- 基于角色的权限控制（admin、librarian、student）
- 用户信息管理

**角色权限**：
- **管理员（admin）**：系统最高权限，可进行所有操作
- **图书管理员（librarian）**：可进行图书管理和借阅操作，无系统配置权限
- **学生（student）**：可进行图书查询、借阅、归还、续借和个人记录查询

### 4. 数据统计模块（dashboard）⭐

**功能**：提供系统运营数据的统计分析和可视化展示

#### 4.1 功能特性

- **概览统计**：系统核心指标快速展示
  - 图书总数、可借数量、总馆藏
  - 用户总数、活跃用户数
  - 当前借阅数、逾期数
  - 今日借阅/归还统计

- **图书统计**：
  - 图书总数、可借数量、已借数量
  - 各分类图书数量分布（饼图）
  - 热门图书排行（按借阅次数）

- **用户统计**：
  - 注册用户总数
  - 活跃用户数（最近30天内有借阅记录）
  - 逾期用户数
  - 用户借阅量排行

- **借阅趋势分析**：
  - 按日/周/月聚合的借阅与归还趋势（折线图）
  - 借阅状态分布（柱状图）
  - 支持自定义时间范围

#### 4.2 API接口

**权限**：所有统计接口仅限管理员（admin）访问

1. **概览统计**
   - URL：`GET /api/reports/summary`
   - 返回：系统核心指标概览
   - 示例响应：
   ```json
   {
     "books": {
       "total": 150,
       "total_copies": 500,
       "available_copies": 320,
       "borrowed_copies": 180
     },
     "users": {
       "total": 200,
       "active": 85
     },
     "borrows": {
       "current": 180,
       "overdue": 5,
       "today_borrows": 12,
       "today_returns": 8
     }
   }
   ```

2. **图书统计**
   - URL：`GET /api/reports/books`
   - 返回：图书总数、可借数量、分类分布、热门图书排行
   - 示例响应：
   ```json
   {
     "total_books": 150,
     "total_copies": 500,
     "available_copies": 320,
     "borrowed_copies": 180,
     "category_distribution": [
       {
         "category": "计算机",
         "count": 45,
         "total_copies": 150,
         "available_copies": 100
       }
     ],
     "popular_books": [
       {
         "id": 1,
         "title": "Python编程",
         "author": "作者名",
         "isbn": "978-xxx",
         "category": "计算机",
         "borrow_count": 25,
         "available_copies": 3,
         "total_copies": 5
       }
     ]
   }
   ```

3. **用户统计**
   - URL：`GET /api/reports/users`
   - 返回：注册用户数、活跃用户数、逾期用户数、借阅量排行
   - 示例响应：
   ```json
   {
     "total_users": 200,
     "active_users": 85,
     "overdue_users": 3,
     "role_distribution": [
       {
         "role": "student",
         "role_display": "学生",
         "count": 180
       }
     ],
     "top_borrowers": [
       {
         "id": 1,
         "username": "student001",
         "student_id": "2021001",
         "role": "student",
         "borrow_count": 15
       }
     ]
   }
   ```

4. **借阅趋势**
   - URL：`GET /api/reports/borrows?period=day&days=30`
   - 查询参数：
     - `period`：统计周期，可选值：`day`（日）、`week`（周）、`month`（月），默认 `day`
     - `days`：统计天数范围，默认 30
   - 返回：按周期聚合的借阅与归还趋势数据
   - 示例响应：
   ```json
   {
     "period": "day",
     "days": 30,
     "summary": {
       "total_borrows": 150,
       "total_returns": 120,
       "current_borrows": 180,
       "overdue_count": 5,
       "total_fines": 25.50
     },
     "borrow_trend": [
       {
         "date": "2025-01-01",
         "count": 5
       }
     ],
     "return_trend": [
       {
         "date": "2025-01-01",
         "count": 3
       }
     ],
     "status_distribution": {
       "borrowed": 180,
       "returned": 500,
       "overdue": 5
     }
   }
   ```

#### 4.3 可视化展示

Dashboard模块提供了丰富的数据可视化展示：

1. **概览卡片**：4个核心指标卡片，实时展示系统状态
2. **借阅趋势图**：折线图展示借阅与归还趋势，支持按日/周/月切换
3. **分类分布图**：饼图展示图书分类分布
4. **热门图书排行**：列表展示借阅次数最多的图书
5. **用户借阅量排行**：列表展示借阅量最多的用户
6. **状态分布图**：柱状图展示借阅状态分布

**访问方式**：
- 管理员登录后访问首页 `/` 即可看到完整的统计Dashboard
- 普通用户访问首页显示欢迎页面

#### 4.4 使用说明

1. **查看统计Dashboard**：
   - 使用管理员账户登录系统
   - 访问首页 `/`，系统会自动识别管理员身份并显示统计页面

2. **切换统计周期**：
   - 在借阅趋势图表上方，选择"按日"、"按周"或"按月"来切换统计周期

3. **API调用示例**：
   ```javascript
   // 获取概览统计
   fetch('/api/reports/summary', {
     credentials: 'include'
   })
   .then(response => response.json())
   .then(data => console.log(data));

   // 获取借阅趋势（按周统计，最近60天）
   fetch('/api/reports/borrows?period=week&days=60', {
     credentials: 'include'
   })
   .then(response => response.json())
   .then(data => console.log(data));
   ```

## 安全特性

### 1. 权限控制（RBAC）

- **后端校验**：所有API接口在执行业务逻辑前，严格校验用户权限
- **前端控制**：根据用户角色动态展示或隐藏功能入口
- **角色定义**：admin（管理员）、librarian（图书管理员）、student（学生）

### 2. 会话安全

- 浏览器关闭时会话自动过期
- 30分钟无操作自动登出
- 每次请求更新会话过期时间
- 防止会话固定攻击
- HttpOnly Cookie防止XSS窃取会话

### 3. XSS攻击防护 ⭐

系统实现了多层XSS防护机制：

#### 3.1 输入过滤
- **后端过滤**：使用`apps.utils.xss_protection`模块清理用户输入
- **危险字符检测**：自动识别和记录可疑的XSS攻击尝试
- **输入验证**：严格验证所有用户输入的类型、长度和格式

#### 3.2 输出转义
- **Django模板转义**：模板引擎默认对所有变量进行HTML转义
- **JavaScript转义**：Dashboard等页面使用`escapeHtml()`函数转义动态内容
- **API响应清理**：确保API返回的数据在前端渲染时被正确转义

#### 3.3 安全响应头
- **X-XSS-Protection**: `1; mode=block` - 启用浏览器XSS过滤器
- **X-Content-Type-Options**: `nosniff` - 防止MIME类型嗅探
- **Content-Security-Policy (CSP)**: 限制资源加载来源，防止内联脚本执行
- **Referrer-Policy**: 控制Referer头信息泄露
- **Permissions-Policy**: 禁用不必要的浏览器API

#### 3.4 安全中间件
- **XSSProtectionMiddleware**: 自动为所有响应添加安全头
- **InputSanitizationMiddleware**: 检测和记录可疑的XSS攻击尝试

#### 3.5 测试工具
- **单元测试**: `apps/utils/tests.py` - 测试XSS防护函数
- **手动测试脚本**: `test_xss_attack.py` - 模拟真实XSS攻击场景

### 4. SQL注入防护

- 使用Django ORM进行所有数据库操作，自动参数化查询
- 禁止拼接SQL语句
- 严格的输入验证和类型检查

### 5. CSRF攻击防护

- CSRF Token保护所有修改类操作（POST、PUT、DELETE）
- 自动验证Token有效性
- AJAX请求支持CSRF保护

### 6. 数据安全

- 敏感数据加密存储（可扩展）
- 密码使用bcrypt/PBKDF2哈希
- 数据库连接加密（可配置）

### 7. 事务支持

- 借阅和归还操作使用数据库事务，确保数据一致性
- 使用InnoDB存储引擎支持事务

## XSS防护使用指南

### 开发者指南

在开发新功能时，请遵循以下XSS防护最佳实践：

#### 1. 后端开发

```python
from apps.utils.xss_protection import clean_input, escape_html

# 清理用户输入
user_input = request.POST.get('title')
cleaned_input = clean_input(user_input, max_length=200)

# 保存到数据库
book.title = cleaned_input
book.save()
```

#### 2. 前端模板

```django
{# Django模板会自动转义，无需额外处理 #}
<h1>{{ book.title }}</h1>

{# 如果确实需要输出HTML，请谨慎使用|safe #}
<div>{{ sanitized_html|safe }}</div>
```

#### 3. JavaScript开发

```javascript
// 使用escapeHtml函数转义用户数据
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 在使用innerHTML前转义数据
container.innerHTML = `<h1>${escapeHtml(userInput)}</h1>`;
```

### 测试XSS防护

#### 自动化测试

```bash
# 运行单元测试
python manage.py test apps.utils.tests

# 运行手动测试脚本
python test_xss_attack.py
```

#### 手动测试

尝试在输入框中输入以下XSS payload：

```html
<script>alert('XSS')</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
javascript:alert(1)
```

预期结果：
- ✓ 输入被正确转义或过滤
- ✓ 页面不执行恶意脚本
- ✓ 开发者工具中可以看到转义后的内容

## 项目结构

```
Process/
├── apps/                    # 应用模块
│   ├── accounts/           # 用户管理
│   ├── library/            # 图书管理
│   ├── borrowing/          # 借阅管理
│   └── dashboard/          # 数据统计（Dashboard模块）
├── core/                   # 项目核心配置
│   ├── settings.py        # 项目设置
│   ├── urls.py            # URL路由配置
│   └── wsgi.py            # WSGI配置
├── templates/              # 模板文件
│   ├── base.html          # 基础模板
│   ├── dashboard/         # Dashboard模板
│   ├── library/           # 图书管理模板
│   └── borrowing/         # 借阅管理模板
├── static/                # 静态文件
├── manage.py              # Django管理脚本
├── README.md             # 项目说明文档
├── Interface.md          # API接口文档
└── 校园图书借阅管理系统功能需求分析.md  # 需求分析文档
```

## 开发规范

### 代码规范

- 遵循PEP 8 Python代码规范
- 使用Django最佳实践
- 完善的代码注释和文档字符串
- 使用SOLID原则设计代码结构

### 数据库设计

- 使用Django ORM进行数据库操作
- 合理设计索引提升查询性能
- 使用事务保证数据一致性

### 性能优化

- 使用`select_related`和`prefetch_related`优化ORM查询
- 对高频查询字段建立索引
- 使用数据库连接池（CONN_MAX_AGE）

## 安全最佳实践

### 生产环境配置

在部署到生产环境前，请确保：

1. **关闭DEBUG模式**
```python
DEBUG = False
```

2. **使用强密钥**
```python
SECRET_KEY = os.environ.get('SECRET_KEY')  # 从环境变量读取
```

3. **配置ALLOWED_HOSTS**
```python
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
```

4. **启用HTTPS**
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

5. **加强CSP策略**
```python
# 移除'unsafe-inline'，使用nonce或hash
CSP_SCRIPT_SRC = ("'self'", "https://cdn.example.com")
```

### 安全监控

系统会自动记录以下安全事件：

- 可疑的XSS攻击尝试
- 失败的登录尝试
- 权限验证失败
- CSRF Token验证失败

日志文件位置：查看Django的logging配置

### 安全更新

定期更新依赖包以修复安全漏洞：

```bash
pip install --upgrade django mysqlclient
pip list --outdated
```

## 后续改进方向

1. ✅ **XSS防护**：完整的XSS攻击防护机制（已完成）
2. **数据加密**：对敏感字段（学号、手机号等）进行加密存储
3. **审计日志**：记录关键操作的审计日志
4. **通知系统**：集成邮件/短信通知，提醒用户逾期
5. **缓存优化**：使用Redis缓存热点数据
6. **API版本控制**：为API接口添加版本前缀
7. **WAF集成**：集成Web应用防火墙，增强安全防护
8. **安全扫描**：定期进行自动化安全扫描

## 许可证

本项目为校园图书借阅管理系统，仅供学习和研究使用。

## 联系方式

如有问题或建议，请联系项目维护者。

---

**最后更新**：2025年11月

