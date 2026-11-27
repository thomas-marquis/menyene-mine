import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Navbar, Container, Nav, Badge } from 'react-bootstrap'
import { useAppDispatch, useAppSelector } from '../../../store'
import { selectStats } from '../../../store/stats/selectors'
import { getAllStats } from '../../../store/stats'

const formatCount = (count: number): string => {
  return count > 99 ? '99+' : count.toString()
}

const REFRESH_INTERVAL_MS = 30000 // 30 seconds

export const Header = () => {
  const dispatch = useAppDispatch()
  const stats = useAppSelector(selectStats)

  useEffect(() => {
    const fetchStats = () => {
      dispatch(getAllStats())
    }

    fetchStats()

    const intervalId = setInterval(fetchStats, REFRESH_INTERVAL_MS)

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        fetchStats()
      }
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      clearInterval(intervalId)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [])

  return (
    <Navbar expand='lg' className='bg-white shadow-sm' style={{ padding: '1rem 0' }}>
      <Container>
        <Navbar.Brand
          as={Link}
          to='/'
          className='fw-semibold'
          style={{ color: '#2c3e50', fontSize: '1.5rem' }}
        >
          Menyene Mine
        </Navbar.Brand>
        <Navbar.Toggle aria-controls='basic-navbar-nav' />
        <Navbar.Collapse id='basic-navbar-nav' className='justify-content-end'>
          <Nav className='gap-3'>
            <Nav.Link
              as={Link}
              to='/'
              className='text-secondary fw-medium d-flex align-items-center gap-1'
              style={{ color: '#7f8c8d' }}
            >
              Recipes
              {stats.recipes > 0 && (
                <Badge bg='primary' className='ms-1'>
                  {formatCount(stats.recipes)}
                </Badge>
              )}
            </Nav.Link>
            <Nav.Link
              as={Link}
              to='/calendar'
              className='text-secondary fw-medium d-flex align-items-center gap-1'
              style={{ color: '#7f8c8d' }}
            >
              Calendar
            </Nav.Link>
            <Nav.Link
              as={Link}
              to='/recipes/drafts'
              className='text-secondary fw-medium d-flex align-items-center gap-1'
              style={{ color: '#7f8c8d' }}
            >
              Drafts
              {stats.pendingDrafts > 0 && (
                <Badge bg='warning' className='ms-1'>
                  {formatCount(stats.pendingDrafts)}
                </Badge>
              )}
            </Nav.Link>
            <Nav.Link
              as={Link}
              to='/groceries'
              className='text-secondary fw-medium d-flex align-items-center gap-1'
              style={{ color: '#7f8c8d' }}
            >
              Grocery List
              {stats.uncheckedGroceries > 0 && (
                <Badge bg='info' className='ms-1'>
                  {formatCount(stats.uncheckedGroceries)}
                </Badge>
              )}
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  )
}
