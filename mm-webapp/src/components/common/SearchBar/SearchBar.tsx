import { type ChangeEvent, type KeyboardEvent } from 'react'
import { Form, InputGroup } from 'react-bootstrap'

/**
 * Props for the SearchBar component
 */
interface SearchBarProps {
  /** Current search query value */
  value: string
  /** Callback when the search query changes */
  onChange: (value: string) => void
  /** Optional callback when the search form is submitted (e.g., on Enter key or button click) */
  onSubmit?: (value: string) => void
  /** Placeholder text for the search input */
  placeholder?: string
  /** Whether the search input is disabled */
  disabled?: boolean
  /** Additional CSS class name for the form container */
  className?: string
}

/**
 * SearchBar - A reusable search input component with optional submit button.
 *
 * Features:
 * - Controlled input with value and onChange props
 * - Optional form submission with onSubmit callback
 * - Supports Enter key for submission
 * - Disabled state
 * - Customizable placeholder
 *
 * @example
 * // Basic search with onChange only
 * <SearchBar value={query} onChange={setQuery} placeholder="Search..." />
 *
 * @example
 * // Search with form submission
 * <SearchBar
 *   value={query}
 *   onChange={setQuery}
 *   onSubmit={(value) => performSearch(value)}
 *   placeholder="Search recipes..."
 * />
 */
export const SearchBar = ({
  value,
  onChange,
  onSubmit,
  placeholder = 'Search...',
  disabled = false,
  className = '',
}: SearchBarProps) => {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && onSubmit) {
      e.preventDefault()
      onSubmit(value)
    }
  }

  const handleFormSubmit = (e: React.SubmitEvent) => {
    if (onSubmit) {
      e.preventDefault()
      onSubmit(value)
    }
  }

  return (
    <Form onSubmit={handleFormSubmit} className={className}>
      <InputGroup>
        <Form.Control
          type='text'
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
        />
        {onSubmit && (
          <button type='submit' className='btn btn-primary' disabled={disabled || !value.trim()}>
            <i className='bi bi-search'></i>
          </button>
        )}
      </InputGroup>
    </Form>
  )
}
