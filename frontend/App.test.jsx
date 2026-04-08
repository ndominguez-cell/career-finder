import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App Component', () => {
    it('renders the main heading', () => {
        render(<App />);
        const heading = screen.getByRole('heading', { level: 1 });
        expect(heading).toBeInTheDocument();
    });

    it('should have a specific text content', () => {
        render(<App />);
        // Replace 'Vite + React' with whatever text is expected in your App component
        const linkElement = screen.getByText(/Vite \+ React/i);
        expect(linkElement).toBeInTheDocument();
    });
});