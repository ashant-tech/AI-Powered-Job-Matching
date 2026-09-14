import { render, screen } from '@testing-library/react'
import Home from '../app/page'

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Home />)
    const heading = screen.getByText('AI-Powered Job Matching')
    expect(heading).toBeInTheDocument()
  })

  it('renders the get started button', () => {
    render(<Home />)
    const button = screen.getByText('Get Started')
    expect(button).toBeInTheDocument()
  })

  it('renders the sign in button', () => {
    render(<Home />)
    const button = screen.getByText('Sign In')
    expect(button).toBeInTheDocument()
  })
})
