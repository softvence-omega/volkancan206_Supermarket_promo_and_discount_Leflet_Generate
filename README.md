# Supermarket Promotional Flyer Generator

An AI-powered promotional flyer generator for supermarkets and grocery stores. This FastAPI-based application uses Google's Generative AI (Gemini) to create professional marketing flyers with product information, pricing, and branding.

## 🚀 Features

- **AI-Powered Design**: Generates professional supermarket flyers using Google Gemini AI
- **Customizable Themes**: Multiple design themes and layouts to match your brand
- **Product Integration**: Automatic product placement with images, pricing, and discount information
- **Logo Integration**: Seamlessly integrates your supermarket logo into the flyer design
- **Multiple Formats**: Outputs both PDF and image formats for versatile usage
- **Campaign Management**: Support for campaign dates, contact information, and promotional messages
- **Price Accuracy**: Ensures exact pricing display with old/new price comparisons and discount percentages
- **Flexible Layout**: Supports different grid layouts (2x2, 3x2, etc.) based on product count

## 🛠 Technology Stack

- **Backend**: FastAPI
- **AI/ML**: Google Generative AI (Gemini)
- **Image Processing**: Pillow (PIL)
- **File Upload**: Cloudinary integration
- **Containerization**: Docker & Docker Compose
- **Database**: File-based storage for generated flyers
- **Logging**: Structured logging with Python logging module

## 📋 Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- Google AI API key
- Cloudinary account (optional, for image hosting)

## 🔧 Installation & Setup

### Method 1: Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Roksana18cse04/Supermarket_promo_and_discount_Leflet_Generate.git
   cd Supermarket_promo_and_discount_Leflet_Generate
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_ai_api_key_here
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret
   ```

5. **Run the application**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```


## 🚀 Usage

### API Endpoints

The application runs on `http://localhost:8000` (or `http://localhost:8010` with Docker Compose)

#### Main Endpoints:
- `GET /` - Welcome message and API status
- `POST /api/generate-flyer` - Generate promotional flyer

#### Interactive API Documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Request Format

Send a POST request to `/api/generate-flyer` with the following JSON structure:

```json
{
  "supermarket_name": "Fresh Market",
  "why_this_campaign": "Weekly Special Offers",
  "supermarket_address": "123 Main Street, City, State",
  "campaign_start_date": "2025-01-01",
  "campaign_end_date": "2025-01-07",
  "supermarket_logo_url": "https://example.com/logo.png",
  "products": [
    {
      "name": "Organic Bananas",
      "secondary_name": "Fresh Ripe Bananas - 1kg",
      "old_price": 5.0,
      "new_price": 3.5,
      "discount": 1.5,
      "image_url": "https://example.com/banana.png",
      "currency": "USD"
    }
  ],
  "products_per_page": 4,
  "template_instruction": "Create a vibrant, modern design",
  "theme_style": "Modern and Clean",
  "phone_number": "555-0123",
  "email": "info@freshmarket.com"
}
```

### Response Format

```json
{
  "success": true,
  "message": "Flyers generated successfully",
  "flyers_generated": 2,
  "pdf_url": "http://localhost:8000/outputs/flyer_abc123.pdf",
  "img_urls": [
    "http://localhost:8000/outputs/flyer_abc123_page1.png",
    "http://localhost:8000/outputs/flyer_abc123_page2.png"
  ]
}
```

## 📁 Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── logger_config.py        # Logging configuration
│   ├── routes/
│   │   └── flyer.py           # Flyer generation routes
│   ├── schemas/
│   │   └── Campaign_Info.py   # Pydantic models for request/response
│   └── services/
│       ├── __init__.py
│       ├── flyer_service.py   # Core flyer generation logic
│       ├── leaflet_generator.py # Leaflet creation service
│       ├── product_name_image.py # Product image processing
│       ├── save_image.py      # Image saving utilities
│       └── upload.py          # File upload handling
├── logs/
│   └── app.log                # Application logs
├── outputs/                   # Generated flyers and PDFs
├── requirements.txt          # Python dependencies
└── README.md                # Project documentation
```

## ⚙ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google AI API key for Gemini model | Yes |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name for image hosting | Optional |
| `CLOUDINARY_API_KEY` | Cloudinary API key | Optional |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | Optional |

### Application Settings

Key configuration options in `app/config.py`:
- Output directory for generated files
- Image processing parameters
- API rate limiting settings
- Logging levels

## 🎨 Customization

### Themes and Styles
The application supports various theme styles:
- Modern and Clean
- Vibrant and Colorful  
- Classic Professional
- Seasonal Themes

### Layout Options
- Grid layouts: 2x2, 3x2, 4x2, etc.
- Product cards with integrated backgrounds
- Logo positioning options
- Price display formats

### Template Instructions
Provide custom template instructions to guide the AI:
- Design preferences
- Color schemes
- Typography choices
- Special requirements

## 🛠 Development

### Running in Development Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```


### Logging

Logs are stored in `logs/app.log` and include:
- Request/response details
- AI generation process
- Error tracking
- Performance metrics


