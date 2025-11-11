-- ============================================================================
-- Script de migración para PostgreSQL
-- Agregar columna 'status' a tabla users_medisupply
-- ============================================================================

BEGIN;

-- Agregar columna status
ALTER TABLE users_medisupply 
ADD COLUMN IF NOT EXISTS status VARCHAR(50) NULL;

-- Agregar comentario a la columna
COMMENT ON COLUMN users_medisupply.status IS 
'Estado del cliente: APROBADO (asignado a vendedor), RECHAZADO (rechazado por admin), NULL (pendiente)';

-- Crear índice para mejorar búsquedas por status (opcional)
CREATE INDEX IF NOT EXISTS idx_users_medisupply_status ON users_medisupply(status);

COMMIT;

-- Verificar
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'users_medisupply' 
  AND column_name = 'status';

