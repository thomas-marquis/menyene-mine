import { type ReactNode, useEffect, useCallback } from 'react';
import { Modal as BootstrapModal } from 'react-bootstrap';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  title?: string;
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  size?: 'sm' | 'lg' | 'xl';
}

export const Modal = ({
  isOpen,
  onClose,
  children,
  title,
  closeOnOverlayClick = true,
  closeOnEscape = true,
  size,
}: ModalProps) => {
  // Handle escape key
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === 'Escape' && closeOnEscape && isOpen) {
        onClose();
      }
    },
    [onClose, closeOnEscape, isOpen]
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, handleKeyDown]);

  return (
    <BootstrapModal
      show={isOpen}
      onHide={onClose}
      backdrop={closeOnOverlayClick ? true : 'static'}
      keyboard={closeOnEscape}
      size={size}
      centered
      onClick={(e: React.MouseEvent<HTMLDivElement>) => {
        if (e.target === e.currentTarget && closeOnOverlayClick) {
          onClose();
        }
      }}
      dialogClassName="modal-dialog-centered"
      contentClassName="border-0"
    >
      {title && (
        <BootstrapModal.Header closeButton closeVariant="white">
          <BootstrapModal.Title>{title}</BootstrapModal.Title>
        </BootstrapModal.Header>
      )}
      <BootstrapModal.Body>{children}</BootstrapModal.Body>
    </BootstrapModal>
  );
};
