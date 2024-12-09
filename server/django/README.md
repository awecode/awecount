# Awecount

<div align="center">

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

</div>

Awecount is a powerful, open-source accounting software designed as a modern alternative to QuickBooks. Built with Python and Django, it provides a robust platform for managing your business finances with ease.

## Features

- **Double Entry Accounting**: Full support for double-entry bookkeeping system
- **Multi-Company Support**: Manage multiple companies from a single installation
- **Bank Reconciliation**: Easily reconcile bank statements with your books
- **Financial Reports**: Generate essential financial reports
  - Balance Sheet
  - Profit & Loss Statement
  - Trial Balance
  - Cash Flow Statement
- **Tax Management**: Built-in tax calculations and reporting
- **Product Management**: Inventory tracking and product management
- **Voucher System**: Support for various voucher types
  - Journal Vouchers
  - Purchase Vouchers
  - Sales Vouchers
  - Payment Vouchers
  - Receipt Vouchers
- **Multi-Currency**: Handle transactions in multiple currencies
- **User Management**: Role-based access control
- **Audit Trail**: Track all changes with detailed audit logs
- **Automated Backups**: Scheduled backups to secure cloud storage

## Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 7+
- Node.js 22+ (for frontend)

## Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/awecount.git
   cd awecount
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Run the development server:

   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to access the application.

## Development Setup

For development, you'll need to set up both backend and frontend environments:

### Backend Setup

```bash
# Install development dependencies
pip install -r requirements/dev.txt

# Run tests
python manage.py test

# Run with debug mode
DEBUG=True python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
pnpm install
pnpm run dev
```

## Deployment

Refer to our [Deployment Guide](docs/deployment.md) for production deployment instructions.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add some amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

## Documentation

- [User Guide](docs/user-guide.md)
- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)

## Support

- [Issue Tracker](https://github.com/awecode/awecount/issues)
- [Discussions](https://github.com/awecode/awecount/discussions)

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape Awecount
- Built with [Django](https://www.djangoproject.com/) and [React](https://reactjs.org/)
- Inspired by various open-source accounting projects

---

<div align="center">
Made with ❤️ by the Awecount Team
</div>
