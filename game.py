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
            # Sombra
            pygame.draw.ellipse(ventana, (30, 30, 30), (x_pantalla + 10, self.y + self.alto - 5, self.ancho - 20, 10))
            # Cuerpo
            pygame.draw.rect(ventana, self.color, (x_pantalla, self.y, self.ancho, self.alto), border_radius=10)
            # Ventana
            pygame.draw.rect(ventana, (180, 220, 255), (x_pantalla + 15, self.y + 8, self.ancho - 30, self.alto - 16), border_radius=5)
            # Ruedas
            pygame.draw.circle(ventana, NEGRO, (int(x_pantalla + 15), int(self.y + self.alto)), 8)
            pygame.draw.circle(ventana, NEGRO, (int(x_pantalla + self.ancho - 15), int(self.y + self.alto)), 8)
            # Luces delanteras
            pygame.draw.circle(ventana, (255, 255, 100), (int(x_pantalla + self.ancho), int(self.y + 10)), 4)
            pygame.draw.circle(ventana, (255, 255, 100), (int(x_pantalla + self.ancho), int(self.y + self.alto - 10)), 4)
            # Nitro (igual que antes)
            if self.es_jugador and self.usando_nitro:
                for _ in range(3):
                    x_offset = random.randint(-20, -10)
                    y_offset = random.randint(-5, 5)
                    pygame.draw.circle(ventana, AMARILLO, (int(x_pantalla + x_offset), int(self.y + self.alto//2 + y_offset)), 3)
        
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
        self.fuente = pygame.font.SysFont("consolas", 36, bold=True)
        self.fuente_grande = pygame.font.SysFont("consolas", 48, bold=True)
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
        self.dibujar_fondo()
        self.dibujar_carretera(self.camara_x)
        
        # Actualizar posición de la cámara para seguir al jugador suavemente
        objetivo_x = self.jugador.x - ANCHO//4
        self.camara_x += (objetivo_x - self.camara_x) * 0.1

        # Dibujar meta animada
        x_meta = self.meta - self.camara_x
        if 0 <= x_meta <= ANCHO:
            color_meta = BLANCO if (pygame.time.get_ticks() // 300) % 2 == 0 else AMARILLO
            pygame.draw.line(ventana, color_meta, (x_meta, 0), (x_meta, ALTO), 8)
            meta_texto = self.fuente_grande.render("META", True, color_meta)
            ventana.blit(meta_texto, (x_meta - 60, 10))

        # Dibujar autos con offset de cámara
        self.jugador.dibujar(self.camara_x)
        for competidor in self.competidores:
            competidor.dibujar(self.camara_x)

        # Mostrar información (HUD)
        if self.jugando:
            vel_texto = self.fuente.render(f"Velocidad: {int(self.jugador.velocidad * 10)} km/h", True, BLANCO)
            ventana.blit(vel_texto, (10, 10))
            tiempo_actual = (pygame.time.get_ticks() - self.tiempo_inicio) / 1000
            tiempo_texto = self.fuente.render(f"Tiempo: {tiempo_actual:.1f}s", True, BLANCO)
            ventana.blit(tiempo_texto, (ANCHO - 250, 10))
            controles = self.fuente.render("SHIFT para NITRO", True, AMARILLO)
            ventana.blit(controles, (10, 80))
            score_texto = self.fuente.render(f"Score: {self.jugador.score}", True, BLANCO)
            ventana.blit(score_texto, (10, 120))
            distancia = max(0, int((self.meta - self.jugador.x) / 10))
            dist_texto = self.fuente.render(f"Distancia a meta: {distancia}m", True, BLANCO)
            ventana.blit(dist_texto, (ANCHO - 250, 40))
        else:
            texto = self.fuente_grande.render(self.ganador, True, BLANCO)
            ventana.blit(texto, (ANCHO//2 - 200, ALTO//2 - 40))
            if self.mejor_tiempo < float('inf'):
                mejor_tiempo_texto = self.fuente.render(f"Mejor tiempo: {self.mejor_tiempo:.1f}s", True, BLANCO)
                ventana.blit(mejor_tiempo_texto, (ANCHO//2 - 150, ALTO//2 + 20))
            reiniciar_texto = self.fuente_grande.render("Presiona ESPACIO para reiniciar", True, AMARILLO)
            ventana.blit(reiniciar_texto, (ANCHO//2 - 320, ALTO//2 + 80))

    def dibujar_fondo(self):
        # Degradado de cielo a suelo
        for y in range(ALTO):
            if y < ALTO // 2:
                # Cielo azul degradado
                color = (
                    int(60 + 80 * (y / (ALTO//2))),
                    int(120 + 100 * (y / (ALTO//2))),
                    int(200 + 55 * (y / (ALTO//2)))
                )
            else:
                # Suelo marrón degradado
                color = (
                    int(80 + 60 * ((y-ALTO//2) / (ALTO//2))),
                    int(60 + 40 * ((y-ALTO//2) / (ALTO//2))),
                    int(40 + 20 * ((y-ALTO//2) / (ALTO//2)))
                )
            pygame.draw.line(ventana, color, (0, y), (ANCHO, y))

    def dibujar_carretera(self, camara_x):
        carretera_y = 0
        carretera_h = ALTO
        carretera_x = 0
        carretera_w = ANCHO
        pygame.draw.rect(ventana, (60, 60, 60), (carretera_x, carretera_y, carretera_w, carretera_h))
        # Líneas centrales discontinuas
        for i in range(0, ANCHO*3, 60):
            x = i - camara_x
            if -30 <= x <= ANCHO:
                pygame.draw.rect(ventana, BLANCO, (x, ALTO//2 - 7, 30, 14), border_radius=7)
        # Bordes de la carretera
        pygame.draw.rect(ventana, (200, 200, 200), (0, 0, 10, ALTO))
        pygame.draw.rect(ventana, (200, 200, 200), (ANCHO-10, 0, 10, ALTO))

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
