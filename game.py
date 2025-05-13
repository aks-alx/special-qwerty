import pygame
import random
import os

# Inicializar Pygame y el mezclador de sonido
pygame.init()
pygame.mixer.init()

# Configuración de la ventana
ANCHO = 800
ALTO = 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Street Racing")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
AMARILLO = (255, 255, 0)
MORADO = (147, 0, 211)

# Configuración del juego
CARRILES = 3
ALTURA_CARRIL = ALTO // CARRILES
VELOCIDAD_FONDO = 5

class Auto:
    def __init__(self, x, y, color, es_jugador=False):
        self.x = x
        self.y = y
        self.ancho = 70
        self.alto = 40
        self.color = color
        self.velocidad = 0
        self.es_jugador = es_jugador
        self.aceleracion = 0.8 if es_jugador else random.uniform(0.3, 0.5)
        self.max_velocidad = 15 if es_jugador else random.uniform(8, 12)
        self.nitro = 100 if es_jugador else 0
        self.usando_nitro = False
        self.score = 0

    def mover(self):
        # Manejo del nitro para el jugador
        if self.es_jugador:
            teclas = pygame.key.get_pressed()
            
            # Activar nitro con SHIFT
            if teclas[pygame.K_LSHIFT] and self.nitro > 0:
                self.usando_nitro = True
                self.nitro = max(0, self.nitro - 1)
            else:
                self.usando_nitro = False
                self.nitro = min(100, self.nitro + 0.2)
            
            # Movimiento básico
            if teclas[pygame.K_RIGHT]:
                boost = 2 if self.usando_nitro else 1
                self.velocidad = min(self.velocidad + self.aceleracion * boost, self.max_velocidad * boost)
            elif teclas[pygame.K_LEFT]:
                self.velocidad = max(self.velocidad - self.aceleracion * 1.5, 0)
            else:
                self.velocidad = max(self.velocidad - self.aceleracion * 0.5, 0)
            
            # Cambio de carril
            if teclas[pygame.K_UP] and self.y > ALTURA_CARRIL:
                self.y -= ALTURA_CARRIL
            elif teclas[pygame.K_DOWN] and self.y < ALTO - ALTURA_CARRIL:
                self.y += ALTURA_CARRIL
        else:
            # IA más inteligente para los competidores
            self.velocidad = min(self.velocidad + self.aceleracion, self.max_velocidad)
            if random.random() < 0.02:  # 2% de probabilidad de cambiar de carril
                nuevo_carril = random.randint(0, CARRILES-1) * ALTURA_CARRIL
                if abs(self.y - nuevo_carril) <= ALTURA_CARRIL:
                    self.y = nuevo_carril
        
        # Actualizar posición
        self.x += self.velocidad
        
        # Aumentar score basado en la velocidad
        if self.es_jugador:
            self.score += int(self.velocidad)

    def dibujar(self, camara_x=0):
        # Ajustar posición con la cámara
        x_pantalla = self.x - camara_x
        
        # Solo dibujar si el auto está en la pantalla
        if -self.ancho <= x_pantalla <= ANCHO:
            # Dibujar sombra
            pygame.draw.ellipse(ventana, (50, 50, 50), 
                              (x_pantalla + 10, self.y + self.alto - 5, self.ancho - 20, 10))
            
            # Dibujar cuerpo principal del auto
            pygame.draw.rect(ventana, self.color, (x_pantalla, self.y, self.ancho, self.alto))
            
            # Detalles del auto
            pygame.draw.rect(ventana, NEGRO, 
                           (x_pantalla + self.ancho - 20, self.y + 5, 15, self.alto - 10))  # Ventana
            pygame.draw.rect(ventana, NEGRO, 
                           (x_pantalla + 5, self.y, 10, self.alto))  # Frente
            
            # Efecto de nitro para el jugador
            if self.es_jugador and self.usando_nitro:
                for _ in range(3):
                    x_offset = random.randint(-20, -10)
                    y_offset = random.randint(-5, 5)
                    pygame.draw.circle(ventana, AMARILLO, 
                                     (int(x_pantalla + x_offset), int(self.y + self.alto//2 + y_offset)), 3)
        
        # Barra de nitro para el jugador (siempre en posición fija en la pantalla)
        if self.es_jugador:
            pygame.draw.rect(ventana, BLANCO, (10, 50, 104, 14), 1)
            pygame.draw.rect(ventana, MORADO, (12, 52, self.nitro, 10))

class Juego:
    def __init__(self):
        self.jugador = Auto(ANCHO//4, ALTO - ALTURA_CARRIL * 2, AZUL, True)
        self.competidores = [
            Auto(ANCHO//4, ALTURA_CARRIL * i, color) 
            for i, color in enumerate([ROJO, VERDE, AMARILLO])
        ]
        self.meta = ANCHO * 3  # Meta más lejana
        self.jugando = True
        self.ganador = None
        self.fuente = pygame.font.Font(None, 36)
        self.camara_x = 0  # Posición de la cámara
        self.tiempo_inicio = pygame.time.get_ticks()
        self.mejor_tiempo = float('inf')

    def actualizar(self):
        self.jugador.mover()
        for competidor in self.competidores:
            competidor.mover()

        # Verificar si alguien ganó
        if self.jugador.x >= self.meta:
            tiempo_final = (pygame.time.get_ticks() - self.tiempo_inicio) / 1000
            self.mejor_tiempo = min(self.mejor_tiempo, tiempo_final)
            self.jugando = False
            self.ganador = f"¡Ganaste! Tiempo: {tiempo_final:.1f}s"
        
        for competidor in self.competidores:
            if competidor.x >= self.meta:
                self.jugando = False
                self.ganador = "¡Perdiste!"

    def dibujar(self):
        ventana.fill(NEGRO)
        
        # Actualizar posición de la cámara para seguir al jugador suavemente
        objetivo_x = self.jugador.x - ANCHO//4  # Mantener el jugador en el primer cuarto de la pantalla
        self.camara_x += (objetivo_x - self.camara_x) * 0.1  # Suavizado del movimiento
        
        # Dibujar efecto de carretera
        segmento_ancho = 200
        inicio_segmento = int(self.camara_x // segmento_ancho) - 1
        fin_segmento = inicio_segmento + (ANCHO // segmento_ancho) + 3
        
        for i in range(inicio_segmento, fin_segmento):
            x = i * segmento_ancho - self.camara_x
            for j in range(CARRILES + 1):
                y = j * ALTURA_CARRIL
                pygame.draw.line(ventana, BLANCO, (x, y), (x + 100, y), 3)
        
        # Dibujar meta
        x_meta = self.meta - self.camara_x
        if 0 <= x_meta <= ANCHO:
            pygame.draw.line(ventana, BLANCO, (x_meta, 0), (x_meta, ALTO), 5)
            meta_texto = self.fuente.render("META", True, BLANCO)
            ventana.blit(meta_texto, (x_meta - 30, 10))
        
        # Dibujar autos con offset de cámara
        self.jugador.dibujar(self.camara_x)
        for competidor in self.competidores:
            competidor.dibujar(self.camara_x)

        # Mostrar información (siempre en posición fija en la pantalla)
        if self.jugando:
            # Mostrar velocidad
            vel_texto = self.fuente.render(f"Velocidad: {int(self.jugador.velocidad * 10)} km/h", True, BLANCO)
            ventana.blit(vel_texto, (10, 10))
            
            # Mostrar tiempo
            tiempo_actual = (pygame.time.get_ticks() - self.tiempo_inicio) / 1000
            tiempo_texto = self.fuente.render(f"Tiempo: {tiempo_actual:.1f}s", True, BLANCO)
            ventana.blit(tiempo_texto, (ANCHO - 200, 10))
            
            # Mostrar controles
            controles = self.fuente.render("SHIFT para NITRO", True, AMARILLO)
            ventana.blit(controles, (10, 80))
            
            # Mostrar score
            score_texto = self.fuente.render(f"Score: {self.jugador.score}", True, BLANCO)
            ventana.blit(score_texto, (10, 120))
            
            # Mostrar distancia a la meta
            distancia = max(0, int((self.meta - self.jugador.x) / 10))
            dist_texto = self.fuente.render(f"Distancia a meta: {distancia}m", True, BLANCO)
            ventana.blit(dist_texto, (ANCHO - 200, 40))
        else:
            texto = self.fuente.render(self.ganador, True, BLANCO)
            ventana.blit(texto, (ANCHO//2 - 150, ALTO//2))
            if self.mejor_tiempo < float('inf'):
                mejor_tiempo_texto = self.fuente.render(f"Mejor tiempo: {self.mejor_tiempo:.1f}s", True, BLANCO)
                ventana.blit(mejor_tiempo_texto, (ANCHO//2 - 150, ALTO//2 + 40))
            reiniciar_texto = self.fuente.render("Presiona ESPACIO para reiniciar", True, BLANCO)
            ventana.blit(reiniciar_texto, (ANCHO//2 - 150, ALTO//2 + 80))

def main():
    reloj = pygame.time.Clock()
    juego = Juego()
    
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return
            if evento.type == pygame.KEYDOWN and not juego.jugando:
                if evento.key == pygame.K_SPACE:
                    juego = Juego()  # Reiniciar juego

        if juego.jugando:
            juego.actualizar()
        
        juego.dibujar()
        pygame.display.flip()
        reloj.tick(60)

if __name__ == "__main__":
    main()
