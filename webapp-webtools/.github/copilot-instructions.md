# Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a React TypeScript web application for file processing tools. The app provides various file manipulation services like merging PDFs, converting documents to PDF, and image processing.

## Architecture
- **Frontend**: React 18 with TypeScript, Vite build tool
- **Routing**: React Router v6 for SPA navigation  
- **Styling**: Tailwind CSS with custom components
- **State Management**: React Context for authentication and toast notifications
- **API**: Axios for HTTP requests to backend services
- **Authentication**: JWT token-based auth with localStorage persistence

## Key Features
- User authentication (login/register) using existing MongoDB backend
- Category-based tool organization (Merge, Convert to PDF)
- File upload with drag & drop support
- Process monitoring with real-time status updates
- Secure file download with temporary links
- Responsive design with modern UI components

## Code Style Guidelines
- Use functional components with hooks
- Prefer TypeScript interfaces over types
- Use proper type annotations for all props and state
- Implement proper error handling with user-friendly messages
- Follow React best practices (proper hook dependencies, etc.)
- Use Tailwind utility classes for styling
- Keep components focused and modular

## File Structure
- `src/pages/` - Route components (Home, Login, Register, Upload, Wait, Download)
- `src/components/` - Reusable UI components (Layout, ProtectedRoute)
- `src/contexts/` - React context providers (Auth, Toast)
- `src/services/` - API service functions
- `src/config/` - Configuration files (tool definitions)

## API Integration
The app communicates with a FastAPI backend running on localhost:8000:
- Authentication endpoints: `/api/register`, `/api/authenticate`
- File processing: `/api/process` (create, get status, download)
- All authenticated requests use Bearer token authorization

## Development Notes
- Backend API uses same authentication system as existing MongoDB project
- File processing is asynchronous with polling-based status updates
- All file uploads are temporary and automatically cleaned up
- Error messages should be user-friendly and actionable
- Process IDs are UUIDs for secure file access
