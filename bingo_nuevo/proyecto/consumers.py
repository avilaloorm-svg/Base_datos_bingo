import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from proyecto.models import PartidaBingo

class BingoConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # 1. Obtenemos el ID de la partida desde la URL
        self.id_partida = self.scope['url_route']['kwargs']['id_partida']
        
        # 2. Consultamos asincrónamente a qué evento de Bingo pertenece esta partida
        self.id_bingo = await self.obtener_id_bingo(self.id_partida)

        # Seguridad: Si la partida no existe, rechazamos la conexión
        if not self.id_bingo:
            await self.close()
            return

        # 3. Nombramos los 3 grupos estratégicos
        self.group_partida = f'bingo_partida_{self.id_partida}'
        self.group_tienda = f'bingo_tienda_{self.id_bingo}'
        self.group_chat = f'bingo_chat_{self.id_bingo}'

        # 4. Inscribimos el navegador del estudiante a los 3 canales
        await self.channel_layer.group_add(self.group_partida, self.channel_name)
        await self.channel_layer.group_add(self.group_tienda, self.channel_name)
        await self.channel_layer.group_add(self.group_chat, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Cuando el estudiante sale de la página, lo damos de baja de los 3 grupos
        if hasattr(self, 'group_partida'):
            await self.channel_layer.group_discard(self.group_partida, self.channel_name)
            await self.channel_layer.group_discard(self.group_tienda, self.channel_name)
            await self.channel_layer.group_discard(self.group_chat, self.channel_name)
    # ================================================
    # RECEPTOR DE MENSAJES (FRONTEND -> BACKEND)
    # ================================================

    async def receive(self, text_data):
        data = json.loads(text_data)
        tipo_evento = data.get('tipo')

        # Si un estudiante escribe en el chat
        if tipo_evento == 'chat':
            # Extraemos su username de la sesión de Django
            usuario = self.scope["user"].username if self.scope["user"].is_authenticated else "Invitado"

            # Repartimos el mensaje a todo el Grupo de Chat
            await self.channel_layer.group_send(
                self.group_chat,
                {
                'type': 'evento_chat',
                'mensaje': data['mensaje'],
                'usuario': usuario
            }
        )

    # ================================================
    # EMISORES A NAVEGADORES (BACKEND -> FRONTEND)
    # ================================================

    # Maneja los mensajes del Chat
    async def evento_chat(self, event):
        await self.send(text_data=json.dumps({
            'canal': 'chat',
            'usuario': event['usuario'],
            'mensaje': event['mensaje']
        }))

    # Maneja los eventos del Juego (Bolas cantadas, Pausas, Ganadores)
    async def evento_partida(self, event):
        await self.send(text_data=json.dumps({
            'canal': 'partida',
            'datos': event['datos']
        }))

    # Maneja los eventos de la Tienda (Stock de cartones agotados)
    async def evento_tienda(self, event):
        await self.send(text_data=json.dumps({
            'canal': 'tienda',
            'datos': event['datos']
        }))

    # ================================================
    # HELPER DE BASE DE DATOS
    # ================================================

    @database_sync_to_async
    def obtener_id_bingo(self, id_partida):
        """Busca el ID del Bingo maestro sin bloquear el hilo asíncrono"""
        try:
            partida = PartidaBingo.objects.get(idpartidabingo=id_partida)
            return partida.idbingo_id
        except PartidaBingo.DoesNotExist:
            return None