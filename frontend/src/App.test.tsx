import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from './App'

describe('App Component', () => {
  it('renders title and subtitle', () => {
    render(<App />)
    expect(screen.getByText('SF Movies')).toBeInTheDocument()
    expect(screen.getByText('Discover movie locations in San Francisco')).toBeInTheDocument()
  })
})
