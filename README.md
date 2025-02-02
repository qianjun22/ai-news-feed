# AI News 24HR

A minimalist, accessible news aggregator for AI-related news and research.

## Progress Log

### February 2, 2024

1. **Load More Functionality**
   - Added "Load More" button for pagination
   - Articles are appended to the list without replacing existing ones
   - Improved article numbering and UI adjustments

2. **UI Enhancements**
   - Removed "TODAY" subtitle for today's articles
   - Ensured dynamic grouping by date

3. **Crawler and Database Updates**
   - Implemented deduplication logic using hashes
   - Updated database schema to include hash columns
   - Enhanced crawler to check for duplicates before saving

### February 1, 2024

1. **Initial Setup**
   - Created basic project structure
   - Set up Supabase integration
   - Implemented responsive layout

2. **Database Schema**
   - Created tables for articles, AI summaries, and audio content
   - Implemented proper relationships and indexes
   - Added RLS policies for security
   - Created sample data for testing

3. **Frontend Development**
   - Implemented minimalist, single-line news layout
   - Added time-based grouping (Today, Yesterday, etc.)
   - Enhanced accessibility with ARIA labels
   - Added visual indicators for news categories
   - Implemented expandable news summaries
   - Matched OpenAI's design aesthetic

4. **Features Implemented**
   - Real-time news fetching from Supabase
   - Fallback to sample data if connection fails
   - Relative time display for recent news
   - Source attribution and direct links
   - Category-based emoji indicators
   - Clickable titles with expandable summaries

## Progress on Development Plan

✅ Phase 1: Basic Setup and Data Structure (100% Complete)
- [x] Project initialization
- [x] Database schema design
- [x] Basic frontend structure
- [x] Supabase integration

🟨 Phase 2: Core Features (70% Complete)
- [x] News display and formatting
- [x] Time-based grouping
- [x] Category indicators
- [x] Expandable summaries
- [x] Load More functionality
- [ ] Search functionality
- [ ] Filtering system

🟦 Phase 3: AI Integration (Pending)
- [ ] AI summaries generation
- [ ] Audio content creation
- [ ] Automated categorization

🟦 Phase 4: Advanced Features (Pending)
- [ ] RSS/JSON feeds
- [ ] API endpoints
- [ ] User preferences

## Project Structure

```
ainews/
├── index.html          # Main HTML file
├── styles.css          # Styling
├── script.js           # Frontend logic
├── config.js           # Supabase configuration (gitignored)
├── config.example.js   # Example configuration
├── assets/
│   └── images/         # Icons and images
├── crawler/            # Crawler scripts
│   ├── main.py         # Main crawler script
│   ├── parsers/        # Parsers for different sources
│   ├── utils/          # Utility functions
│   └── config/         # Crawler configuration
└── database/           # SQL schema files
    ├── 01_articles.sql
    ├── 02_ai_summaries.sql
    ├── 03_audio_content.sql
    └── 04_triggers.sql
```

## Next Steps
1. Implement search functionality
2. Add filtering by category
3. Begin AI integration for summaries
4. Set up RSS/JSON feeds
5. Add dark mode support

## Development
1. Copy `config.example.js` to `config.js` and add your Supabase credentials
2. Copy `crawler/config/settings.example.py` to `crawler/config/settings.py` and add your Supabase credentials
3. Run a local server (e.g., `npm start`)
4. Visit `http://localhost:3000`

## Crawler Setup
1. Install Python dependencies: `pip install -r crawler/requirements.txt`
2. Copy settings: `cp crawler/config/settings.example.py crawler/config/settings.py`
3. Update Supabase credentials in `crawler/config/settings.py`
4. Run crawler: `python -m crawler.main` 