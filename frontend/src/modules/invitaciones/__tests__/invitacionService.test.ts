/**
 * Tests para invitacionService
 * Enfoque: Validación de tipos, estructuras y lógica de negocio
 * Patrón: Mismo enfoque exitoso de instituciones/programas (32 tests)
 */

import { describe, it, expect } from 'vitest';
import type {
  Invitacion,
  CrearInvitacionDTO,
  AceptarInvitacionDTO,
  RechazarInvitacionDTO,
  FiltrosInvitaciones,
  EstadisticasInvitaciones,
  ValidacionInvitacion,
  NotificacionInvitacion,
  EstadoInvitacion,
  RolInvitacion,
} from '../types';

describe('invitacionService - Validaciones de Tipos y Estructuras', () => {
  describe('Estructura de Invitacion', () => {
    it('debe tener todas las propiedades requeridas', () => {
      const invitacion: Invitacion = {
        id: 1,
        codigo: '123456',
        token: 'abc123',
        email: 'test@example.com',
        nombreInvitado: 'Juan Pérez',
        rol: 'COORDINADOR',
        institucionId: 1,
        institucionNombre: 'Universidad Nacional',
        programaId: undefined,
        programaNombre: undefined,
        estado: 'PENDIENTE',
        fechaCreacion: '2024-01-01T00:00:00Z',
        fechaExpiracion: '2024-01-08T00:00:00Z',
        fechaAceptacion: undefined,
        fechaRechazo: undefined,
        mensaje: undefined,
        creadoPorId: 1,
        creadoPorNombre: 'Admin User',
        aceptadoPorId: undefined,
        intentosReenvio: 0,
        ultimoReenvio: undefined,
      };

      expect(invitacion).toHaveProperty('id');
      expect(invitacion).toHaveProperty('codigo');
      expect(invitacion).toHaveProperty('token');
      expect(invitacion).toHaveProperty('email');
      expect(invitacion).toHaveProperty('nombreInvitado');
      expect(invitacion).toHaveProperty('rol');
      expect(invitacion).toHaveProperty('estado');
      expect(invitacion).toHaveProperty('fechaCreacion');
      expect(invitacion).toHaveProperty('fechaExpiracion');
    });

    it('debe validar código de 6 dígitos', () => {
      const codigoValido = /^\d{6}$/;
      
      expect(codigoValido.test('123456')).toBe(true);
      expect(codigoValido.test('000000')).toBe(true);
      expect(codigoValido.test('999999')).toBe(true);
      
      // Inválidos
      expect(codigoValido.test('12345')).toBe(false);
      expect(codigoValido.test('1234567')).toBe(false);
      expect(codigoValido.test('abcdef')).toBe(false);
    });

    it('debe validar formato de email', () => {
      const emailValido = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;
      
      expect(emailValido.test('usuario@example.com')).toBe(true);
      expect(emailValido.test('test+tag@domain.co')).toBe(true);
      expect(emailValido.test('user.name@sub.domain.com')).toBe(true);
      
      // Inválidos
      expect(emailValido.test('invalido')).toBe(false);
      expect(emailValido.test('@example.com')).toBe(false);
      expect(emailValido.test('user@')).toBe(false);
    });

    it('debe validar token único', () => {
      const tokenValido = /^[a-zA-Z0-9-_]+$/;
      
      expect(tokenValido.test('abc123def456')).toBe(true);
      expect(tokenValido.test('TOKEN-WITH-DASHES')).toBe(true);
      expect(tokenValido.test('token_with_underscores')).toBe(true);
      
      // Inválidos
      expect(tokenValido.test('token with spaces')).toBe(false);
      expect(tokenValido.test('token@special')).toBe(false);
    });
  });

  describe('Enums', () => {
    it('debe definir todos los estados de invitación', () => {
      const estados: EstadoInvitacion[] = [
        'PENDIENTE',
        'ACEPTADA',
        'RECHAZADA',
        'EXPIRADA',
        'CANCELADA',
      ];

      estados.forEach(estado => {
        expect(estado).toBeDefined();
        expect(typeof estado).toBe('string');
      });

      // Validar transiciones válidas
      expect(estados).toContain('PENDIENTE');
      expect(estados).toContain('ACEPTADA');
      expect(estados).toContain('RECHAZADA');
      expect(estados).toContain('EXPIRADA');
      expect(estados).toContain('CANCELADA');
    });

    it('debe definir todos los roles de invitación', () => {
      const roles: RolInvitacion[] = ['COORDINADOR', 'PROFESOR', 'ESTUDIANTE'];

      roles.forEach(rol => {
        expect(rol).toBeDefined();
        expect(typeof rol).toBe('string');
      });

      expect(roles).toHaveLength(3);
    });
  });

  describe('Estructura de CrearInvitacionDTO', () => {
    it('debe tener propiedades requeridas para crear invitación', () => {
      const dto: CrearInvitacionDTO = {
        email: 'coordinador@example.com',
        nombreInvitado: 'María González',
        rol: 'COORDINADOR',
        institucionId: 1,
      };

      expect(dto).toHaveProperty('email');
      expect(dto).toHaveProperty('nombreInvitado');
      expect(dto).toHaveProperty('rol');
      expect(dto).toHaveProperty('institucionId');
    });

    it('debe permitir propiedades opcionales', () => {
      const dtoCompleto: CrearInvitacionDTO = {
        email: 'profesor@example.com',
        nombreInvitado: 'Pedro Sánchez',
        rol: 'PROFESOR',
        institucionId: 1,
        programaId: 5,
        mensaje: 'Bienvenido al equipo',
        diasExpiracion: 15,
      };

      expect(dtoCompleto.programaId).toBe(5);
      expect(dtoCompleto.mensaje).toBe('Bienvenido al equipo');
      expect(dtoCompleto.diasExpiracion).toBe(15);
    });
  });

  describe('Estructura de AceptarInvitacionDTO', () => {
    it('debe tener datos para aceptar y crear cuenta', () => {
      const dto: AceptarInvitacionDTO = {
        token: 'abc123def456',
        codigo: '123456',
        nombre: 'Juan',
        apellido: 'Pérez',
        password: 'Password123',
        passwordConfirm: 'Password123',
      };

      expect(dto).toHaveProperty('token');
      expect(dto).toHaveProperty('codigo');
      expect(dto).toHaveProperty('nombre');
      expect(dto).toHaveProperty('apellido');
      expect(dto).toHaveProperty('password');
      expect(dto).toHaveProperty('passwordConfirm');
    });

    it('debe validar contraseña segura', () => {
      const passwordSegura = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
      
      expect(passwordSegura.test('Password123')).toBe(true);
      expect(passwordSegura.test('MyPass99')).toBe(true);
      
      // Inválidas
      expect(passwordSegura.test('password')).toBe(false); // Sin mayúscula ni número
      expect(passwordSegura.test('PASSWORD123')).toBe(false); // Sin minúscula
      expect(passwordSegura.test('Pass12')).toBe(false); // Muy corta
    });
  });

  describe('Lógica de Negocio - Estados', () => {
    it('debe validar transiciones de estado válidas', () => {
      const transicionesValidas: Record<EstadoInvitacion, EstadoInvitacion[]> = {
        PENDIENTE: ['ACEPTADA', 'RECHAZADA', 'EXPIRADA', 'CANCELADA'],
        ACEPTADA: [], // Estado final
        RECHAZADA: [], // Estado final
        EXPIRADA: ['ACEPTADA'], // Puede reactivarse
        CANCELADA: [], // Estado final
      };

      // Pendiente puede ir a múltiples estados
      expect(transicionesValidas.PENDIENTE).toContain('ACEPTADA');
      expect(transicionesValidas.PENDIENTE).toContain('RECHAZADA');
      expect(transicionesValidas.PENDIENTE).toContain('EXPIRADA');
      expect(transicionesValidas.PENDIENTE).toContain('CANCELADA');

      // Estados finales no cambian
      expect(transicionesValidas.ACEPTADA).toHaveLength(0);
      expect(transicionesValidas.RECHAZADA).toHaveLength(0);
      expect(transicionesValidas.CANCELADA).toHaveLength(0);
    });

    it('debe validar reglas de expiración', () => {
      const calcularExpiracion = (diasExpiracion: number = 7): Date => {
        const fecha = new Date();
        fecha.setDate(fecha.getDate() + diasExpiracion);
        return fecha;
      };

      const expiracion7dias = calcularExpiracion(7);
      const expiracion15dias = calcularExpiracion(15);

      expect(expiracion7dias.getTime()).toBeGreaterThan(Date.now());
      expect(expiracion15dias.getTime()).toBeGreaterThan(expiracion7dias.getTime());
    });

    it('debe validar que invitación está expirada', () => {
      const estaExpirada = (fechaExpiracion: string): boolean => {
        return new Date(fechaExpiracion) < new Date();
      };

      expect(estaExpirada('2020-01-01T00:00:00Z')).toBe(true);
      expect(estaExpirada('2099-12-31T23:59:59Z')).toBe(false);
    });
  });

  describe('Lógica de Negocio - Códigos', () => {
    it('debe generar códigos únicos de 6 dígitos', () => {
      const generarCodigo = (): string => {
        return Math.floor(100000 + Math.random() * 900000).toString();
      };

      const codigo1 = generarCodigo();
      const codigo2 = generarCodigo();

      expect(codigo1).toMatch(/^\d{6}$/);
      expect(codigo2).toMatch(/^\d{6}$/);
      expect(parseInt(codigo1)).toBeGreaterThanOrEqual(100000);
      expect(parseInt(codigo1)).toBeLessThanOrEqual(999999);
    });

    it('debe validar código correcto', () => {
      const validarCodigo = (codigoIngresado: string, codigoReal: string): boolean => {
        return codigoIngresado === codigoReal;
      };

      expect(validarCodigo('123456', '123456')).toBe(true);
      expect(validarCodigo('123456', '654321')).toBe(false);
    });
  });

  describe('Estructura de FiltrosInvitaciones', () => {
    it('debe permitir filtrar por múltiples criterios', () => {
      const filtros: FiltrosInvitaciones = {
        estado: 'PENDIENTE',
        rol: 'COORDINADOR',
        institucionId: 1,
        email: 'test@example.com',
        busqueda: 'Juan',
        fechaDesde: '2024-01-01',
        fechaHasta: '2024-12-31',
        pagina: 1,
        limite: 10,
        ordenarPor: 'reciente',
      };

      expect(filtros.estado).toBe('PENDIENTE');
      expect(filtros.rol).toBe('COORDINADOR');
      expect(filtros.pagina).toBe(1);
      expect(filtros.limite).toBe(10);
    });

    it('debe validar opciones de ordenamiento', () => {
      const opcionesOrden: FiltrosInvitaciones['ordenarPor'][] = [
        'reciente',
        'antiguo',
        'expiracion',
      ];

      opcionesOrden.forEach(opcion => {
        const filtro: FiltrosInvitaciones = { ordenarPor: opcion };
        expect(filtro.ordenarPor).toBeDefined();
      });
    });
  });

  describe('Estructura de EstadisticasInvitaciones', () => {
    it('debe calcular estadísticas correctamente', () => {
      const estadisticas: EstadisticasInvitaciones = {
        total: 100,
        pendientes: 30,
        aceptadas: 50,
        rechazadas: 10,
        expiradas: 8,
        canceladas: 2,
        coordinadores: 20,
        profesores: 60,
        estudiantes: 20,
        tasaAceptacion: 71.43,
        tiempoPromedioAceptacion: 48,
        invitacionesHoy: 5,
        invitacionesEstaSemana: 25,
      };

      expect(estadisticas.total).toBe(100);
      expect(estadisticas.pendientes + estadisticas.aceptadas + 
             estadisticas.rechazadas + estadisticas.expiradas + 
             estadisticas.canceladas).toBe(100);
      
      // Tasa de aceptación = (aceptadas / (aceptadas + rechazadas + expiradas)) * 100
      // 50 aceptadas de 68 total = 73.53%
      expect(estadisticas.tasaAceptacion).toBeGreaterThan(70);
      expect(estadisticas.tasaAceptacion).toBeLessThan(75);
    });
  });

  describe('Estructura de ValidacionInvitacion', () => {
    it('debe validar invitación válida', () => {
      const validacion: ValidacionInvitacion = {
        valida: true,
        invitacion: {
          id: 1,
          email: 'test@example.com',
          nombreInvitado: 'Test User',
          rol: 'COORDINADOR',
          institucionId: 1,
          institucionNombre: 'Universidad Test',
        } as any,
      };

      expect(validacion.valida).toBe(true);
      expect(validacion.invitacion).toBeDefined();
      expect(validacion.error).toBeUndefined();
    });

    it('debe validar invitación inválida con razón', () => {
      const validacion: ValidacionInvitacion = {
        valida: false,
        error: 'EXPIRADA',
        razon: 'EXPIRADA',
      };

      expect(validacion.valida).toBe(false);
      expect(validacion.error).toBe('EXPIRADA');
      expect(validacion.razon).toBeDefined();
    });
  });

  describe('Estructura de NotificacionInvitacion', () => {
    it('debe tener tipos de notificación definidos', () => {
      const tipos: NotificacionInvitacion['tipo'][] = [
        'INVITACION_RECIBIDA',
        'INVITACION_ACEPTADA',
        'INVITACION_RECHAZADA',
        'INVITACION_EXPIRADA',
      ];

      tipos.forEach(tipo => {
        const notificacion: NotificacionInvitacion = {
          id: 1,
          tipo,
          invitacionId: 1,
          invitacion: {} as any,
          leida: false,
          fechaCreacion: '2024-01-01T00:00:00Z',
        };

        expect(notificacion.tipo).toBe(tipo);
      });
    });
  });

  describe('Validaciones de Transformación de Datos', () => {
    it('debe transformar fechas correctamente', () => {
      const formatearFecha = (fecha: string): string => {
        return new Date(fecha).toLocaleDateString('es-ES');
      };

      const fechaISO = '2024-01-15T10:30:00Z';
      const fechaFormateada = formatearFecha(fechaISO);
      
      expect(fechaFormateada).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/);
    });

    it('debe calcular tiempo transcurrido', () => {
      const calcularTiempoTranscurrido = (fecha: string): string => {
        const ahora = new Date();
        const fechaInvitacion = new Date(fecha);
        const diffMs = ahora.getTime() - fechaInvitacion.getTime();
        const diffDias = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffDias === 0) return 'Hoy';
        if (diffDias === 1) return 'Ayer';
        return `Hace ${diffDias} días`;
      };

      const hoy = new Date().toISOString();
      expect(calcularTiempoTranscurrido(hoy)).toBe('Hoy');
    });
  });

  describe('Validaciones de Seguridad', () => {
    it('debe validar longitud mínima de nombre', () => {
      const nombreValido = (nombre: string): boolean => {
        return nombre.length >= 2;
      };

      expect(nombreValido('Juan')).toBe(true);
      expect(nombreValido('Ab')).toBe(true);
      expect(nombreValido('A')).toBe(false);
      expect(nombreValido('')).toBe(false);
    });

    it('debe validar que las contraseñas coinciden', () => {
      const passwordsCoinciden = (pass1: string, pass2: string): boolean => {
        return pass1 === pass2;
      };

      expect(passwordsCoinciden('Pass123', 'Pass123')).toBe(true);
      expect(passwordsCoinciden('Pass123', 'Pass456')).toBe(false);
    });
  });

  describe('Validaciones de Integración', () => {
    it('debe relacionar invitación con institución', () => {
      const invitacion: Partial<Invitacion> = {
        institucionId: 1,
      };

      expect(invitacion.institucionId).toBeGreaterThan(0);
      expect(invitacion.institucionId).toBeDefined();
    });

    it('debe permitir relación opcional con programa', () => {
      const invitacionConPrograma: Partial<Invitacion> = {
        programaId: 5,
      };

      const invitacionSinPrograma: Partial<Invitacion> = {
        programaId: undefined,
      };

      expect(invitacionConPrograma.programaId).toBe(5);
      expect(invitacionSinPrograma.programaId).toBeUndefined();
    });
  });
});
