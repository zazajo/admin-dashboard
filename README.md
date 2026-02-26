# 🚀 Enterprise Admin Dashboard

A production-ready, full-stack admin dashboard featuring role-based authentication, CSV/Excel data upload system, and comprehensive audit logging.

## Features

### Authentication & Security
- JWT-based authentication with automatic token refresh
- Role-based access control (Admin, Manager, Viewer)
- Granular permission system
- Secure password hashing
- Token blacklisting on logout
- Protected API endpoints

### User Management
- Complete CRUD operations
- User creation with role assignment
- Bulk user activation/deactivation
- Advanced search and filtering
- User statistics dashboard
- Profile management with password change

### Data Upload System
- CSV/Excel file upload with drag & drop interface
- Automatic data validation (row-by-row)
- Support for multiple encodings (UTF-8, Latin-1, ISO-8859-1)
- Real-time processing with pandas
- Error detection and detailed reporting
- Upload history with success rate tracking
- Handles 10,000+ records efficiently

### Activity Tracking
- Complete audit trail for compliance
- Timeline view of all system actions
- Change tracking (before/after values)
- User attribution for all actions
- Advanced filtering and search
- Export capabilities

### UI/UX
- Modern, clean interface with Tailwind CSS
- Fully responsive design (mobile, tablet, desktop)
- Toast notifications for user feedback
- Loading states and error handling
- Intuitive navigation
- Professional data tables with pagination

---

## Tech Stack

### Backend
- **Framework:** Django 5.0.1
- **API:** Django REST Framework 3.14.0
- **Authentication:** Simple JWT 5.3.1
- **Database:** PostgreSQL (production) / SQLite (development)
- **File Processing:** Pandas 2.1.4
- **File Formats:** OpenPyXL 3.1.2
- **CORS:** Django CORS Headers 4.3.1
- **API Docs:** drf-yasg 1.21.7

### Frontend
- **Framework:** Next.js 14.1.0
- **Language:** TypeScript
- **Styling:** Tailwind CSS 3.4.1
- **State Management:** React Context API
- **HTTP Client:** Axios 1.6.7
- **Icons:** Lucide React 0.323.0
- **Date Formatting:** date-fns 3.3.1

---

## Project Structure

```
admin-dashboard/
├── backend/
│   ├── rb_dashboard/          # Main Django project
│   ├── accounts/              # User authentication & management
│   ├── uploads/               # CSV/Excel upload system
│   ├── audit/                 # Audit logging
│   ├── media/                 # Uploaded files
│   └── requirements.txt       # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── app/              # Next.js pages
    │   ├── components/       # Reusable components
    │   ├── contexts/         # React contexts
    │   ├── services/         # API services
    │   ├── types/            # TypeScript types
    │   └── lib/              # Utilities
    └── package.json          # Node dependencies
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL (for production)

# Backend Setup

Clone the repository

bash   git clone https://github.com/zazajo/admin-dashboard.git
   cd admin-dashboard/backend

Create virtual environment

bash   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies

bash   pip install -r requirements.txt

Set up environment variables

bash   cp .env.example .env
    Edit .env with your settings

Run migrations

bash   python manage.py migrate

Create superuser

bash   python manage.py createsuperuser

Start development server

bash   python manage.py runserver
Backend will run on http://127.0.0.1:8000

# Frontend Setup

Navigate to frontend directory

bash   cd frontend

Install dependencies

bash   npm install

Set up environment variables

bash   cp .env.local.example .env.local
    Edit .env.local with your settings

Start development server

bash   npm run dev
Frontend will run on http://localhost:3000

🔑 Environment Variables
Backend (.env)
envSECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
Frontend (.env.local)
envNEXT_PUBLIC_API_URL=http://127.0.0.1:8000

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get user profile
- `POST /api/auth/change-password/` - Change password

### User Management (Admin only)
- `GET /api/auth/users/` - List all users
- `POST /api/auth/users/create/` - Create new user
- `GET /api/auth/users/{id}/` - Get user details
- `PATCH /api/auth/users/{id}/update/` - Update user
- `DELETE /api/auth/users/{id}/delete/` - Deactivate user
- `GET /api/auth/users/stats/` - Get user statistics

### Data Uploads
- `GET /api/uploads/` - List uploads
- `POST /api/uploads/create/` - Upload CSV/Excel file
- `POST /api/uploads/preview/` - Preview file before upload
- `POST /api/uploads/{id}/process/` - Process uploaded file
- `GET /api/uploads/{id}/records/` - Get upload records
- `GET /api/uploads/stats/` - Get upload statistics
- `DELETE /api/uploads/{id}/delete/` - Delete upload

### Audit Logs
- `GET /api/audit/logs/` - List audit logs
- `GET /api/audit/stats/` - Get audit statistics

Full API documentation available at `http://127.0.0.1:8000/api/docs/`

---

## 👥 User Roles & Permissions

### Admin
- ✅ Full system access
- ✅ Manage all users
- ✅ Upload and process data
- ✅ View audit logs
- ✅ Export reports
- ✅ Delete uploads

### Manager
- ✅ Upload and process data
- ✅ View own uploads
- ✅ Export reports
- ❌ Cannot manage users
- ❌ Cannot view audit logs
- ❌ Cannot delete uploads

### Viewer
- ✅ View dashboard
- ✅ View own profile
- ❌ Read-only access
- ❌ Cannot upload data
- ❌ Cannot manage users

## 🔒 Security Features

- JWT token-based authentication
- CORS protection
- CSRF protection
- SQL injection prevention (Django ORM)
- XSS protection
- Password hashing with Django's PBKDF2
- Rate limiting on API endpoints
- Secure file upload validation
- Environment variable configuration

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@zazajo](https://github.com/zazajo)
- LinkedIn: [Your LinkedIn](www.linkedin.com/in/joseph-edward-94b7a3322)
- Portfolio: [yourwebsite.com](https://joewebs.vercel.app)

---

## 🙏 Acknowledgments

- Django REST Framework documentation
- Next.js documentation
- Tailwind CSS team
- Open source community

---

## 📧 Contact

For questions or support, please reach out:
- Email: josephedward201@gmail.com
- LinkedIn: [Your LinkedIn](www.linkedin.com/in/joseph-edward-94b7a3322)

---

## 🗺️ Roadmap

- [ ] Email notifications for uploads
- [ ] Advanced data visualization with charts
- [ ] Export to PDF reports
- [ ] Two-factor authentication
- [ ] Real-time updates with WebSockets
- [ ] Advanced analytics dashboard
- [ ] API rate limiting improvements
- [ ] Mobile app (React Native)

---

**⭐ Star this repo if you find it helpful!**