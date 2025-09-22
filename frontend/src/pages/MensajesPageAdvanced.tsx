import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useToast } from '../context/ToastContext'
import {
  HiOutlineChatAlt2,
  HiOutlinePaperAirplane,
  HiOutlinePaperClip,
  HiOutlineDotsHorizontal,
  HiOutlineSearch,
  HiOutlinePhone,
  HiOutlineVideoCamera,
  HiOutlineMicrophone,
  HiOutlinePhotograph,
  HiOutlineDocument,
  HiOutlineEmojiHappy,
  HiOutlineCheck,
  HiOutlineCheckCircle,
  HiOutlineUserAdd,
  HiOutlinePencilAlt,
  HiOutlineTrash,
  HiOutlineInformationCircle,
  HiOutlineMoon,
  HiOutlineSun,
  HiOutlineCog,
  HiOutlineArchive,
  HiOutlineStar,
  HiOutlineHeart,
  HiOutlineThumbUp,
  HiOutlineDownload,
  HiOutlineArrowNarrowRight,
  HiOutlineReply,
  HiOutlineX
} from 'react-icons/hi'

interface Contact {
  id: string
  name: string
  avatar: string
  status: 'online' | 'offline' | 'away'
  lastSeen?: string
  unreadCount: number
}

interface Message {
  id: string
  senderId: string
  content: string
  timestamp: string
  type: 'text' | 'image' | 'file' | 'audio'
  status: 'sent' | 'delivered' | 'read'
  replyTo?: string
  edited?: boolean
}

interface ChatRoom {
  id: string
  type: 'direct' | 'group'
  name: string
  participants: string[]
  lastMessage?: Message
  unreadCount: number
  avatar?: string
}

const mockContacts: Contact[] = [
  {
    id: '1',
    name: 'Ana García',
    avatar: 'AG',
    status: 'online',
    unreadCount: 3
  },
  {
    id: '2', 
    name: 'Carlos López',
    avatar: 'CL',
    status: 'away',
    lastSeen: '2h',
    unreadCount: 1
  },
  {
    id: '3',
    name: 'María Rodríguez',
    avatar: 'MR',
    status: 'offline',
    lastSeen: '1d',
    unreadCount: 0
  },
  {
    id: '4',
    name: 'Prof. Hernández',
    avatar: 'PH',
    status: 'online',
    unreadCount: 2
  }
]

const mockChatRooms: ChatRoom[] = [
  {
    id: '1',
    type: 'direct',
    name: 'Ana García',
    participants: ['current-user', '1'],
    unreadCount: 3,
    lastMessage: {
      id: 'm1',
      senderId: '1',
      content: '¿Quieres formar equipo para el proyecto final?',
      timestamp: '2025-09-21T10:30:00Z',
      type: 'text',
      status: 'delivered'
    }
  },
  {
    id: '2',
    type: 'group',
    name: 'Matemáticas Avanzadas',
    participants: ['current-user', '1', '2', '4'],
    unreadCount: 1,
    avatar: 'MA',
    lastMessage: {
      id: 'm2',
      senderId: '4',
      content: 'Recuerden que el examen es el viernes',
      timestamp: '2025-09-21T09:15:00Z',
      type: 'text',
      status: 'read'
    }
  },
  {
    id: '3',
    type: 'direct',
    name: 'Carlos López',
    participants: ['current-user', '2'],
    unreadCount: 0,
    lastMessage: {
      id: 'm3',
      senderId: 'current-user',
      content: '¡Perfecto! Nos vemos mañana',
      timestamp: '2025-09-20T18:45:00Z',
      type: 'text',
      status: 'read'
    }
  }
]

const mockMessages: { [chatId: string]: Message[] } = {
  '1': [
    {
      id: 'm1',
      senderId: '1',
      content: '¡Hola! ¿Cómo vas con el proyecto de React?',
      timestamp: '2025-09-21T10:00:00Z',
      type: 'text',
      status: 'read'
    },
    {
      id: 'm2',
      senderId: 'current-user',
      content: 'Bien, ya tengo la estructura básica. ¿Y tú?',
      timestamp: '2025-09-21T10:05:00Z',
      type: 'text',
      status: 'read'
    },
    {
      id: 'm3',
      senderId: '1',
      content: 'Genial! He estado trabajando en el diseño',
      timestamp: '2025-09-21T10:10:00Z',
      type: 'text',
      status: 'read'
    },
    {
      id: 'm4',
      senderId: '1',
      content: '¿Quieres formar equipo para el proyecto final?',
      timestamp: '2025-09-21T10:30:00Z',
      type: 'text',
      status: 'delivered'
    }
  ]
}

export default function MensajesPageAdvanced() {
  const toast = useToast()
  const [selectedChat, setSelectedChat] = useState<string>('1')
  const [message, setMessage] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [showEmojiPicker, setShowEmojiPicker] = useState(false)
  const [showAttachments, setShowAttachments] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [selectedChat])

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('es-ES', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const formatLastSeen = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Hace unos minutos'
    if (diffInHours < 24) return `Hace ${diffInHours}h`
    return `Hace ${Math.floor(diffInHours / 24)}d`
  }

  const sendMessage = () => {
    if (!message.trim()) return

    const newMessage: Message = {
      id: Date.now().toString(),
      senderId: 'current-user',
      content: message,
      timestamp: new Date().toISOString(),
      type: 'text',
      status: 'sent'
    }

    // Simulate message sending
    toast.success('Enviado', 'Mensaje enviado correctamente')
    setMessage('')
    
    // Focus back to input
    setTimeout(() => {
      inputRef.current?.focus()
    }, 100)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const filteredChats = mockChatRooms.filter(chat =>
    chat.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const selectedChatData = mockChatRooms.find(chat => chat.id === selectedChat)
  const chatMessages = mockMessages[selectedChat] || []

  const getContactInfo = (contactId: string) => {
    return mockContacts.find(c => c.id === contactId)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500'
      case 'away': return 'bg-yellow-500'
      case 'offline': return 'bg-gray-400'
      default: return 'bg-gray-400'
    }
  }

  const emojis = ['😊', '😂', '❤️', '👍', '👎', '😢', '😮', '😡', '🎉', '🔥', '💯', '👏']

  return (
    <div className="h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/50 dark:from-gray-900 dark:via-gray-900 dark:to-blue-950/30 flex">
      {/* Sidebar */}
      <div className="w-80 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-r border-gray-200/50 dark:border-gray-700/50 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200/50 dark:border-gray-700/50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Mensajes</h2>
            <div className="flex items-center space-x-2">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <HiOutlineUserAdd className="w-5 h-5" />
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              >
                <HiOutlineCog className="w-5 h-5" />
              </motion.button>
            </div>
          </div>

          {/* Search */}
          <div className="relative">
            <HiOutlineSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar conversaciones..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Chat List */}
        <div className="flex-1 overflow-y-auto">
          {filteredChats.map((chat) => (
            <motion.div
              key={chat.id}
              whileHover={{ backgroundColor: 'rgba(59, 130, 246, 0.05)' }}
              onClick={() => setSelectedChat(chat.id)}
              className={`p-4 cursor-pointer border-b border-gray-100 dark:border-gray-800 transition-colors ${
                selectedChat === chat.id
                  ? 'bg-blue-50 dark:bg-blue-900/20 border-r-2 border-r-blue-500'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
              }`}
            >
              <div className="flex items-center space-x-3">
                {/* Avatar */}
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold">
                      {chat.avatar || chat.name.split(' ').map(n => n[0]).join('')}
                    </span>
                  </div>
                  {chat.type === 'direct' && (
                    <div className={`absolute -bottom-1 -right-1 w-4 h-4 ${getStatusColor(getContactInfo(chat.participants[1])?.status || 'offline')} rounded-full border-2 border-white dark:border-gray-900`}></div>
                  )}
                </div>

                {/* Chat info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                      {chat.name}
                    </h3>
                    {chat.lastMessage && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {formatTime(chat.lastMessage.timestamp)}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <p className="text-sm text-gray-600 dark:text-gray-400 truncate">
                      {chat.lastMessage?.content || 'Sin mensajes'}
                    </p>
                    {chat.unreadCount > 0 && (
                      <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                        <span className="text-xs font-bold text-white">{chat.unreadCount}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {selectedChatData ? (
          <>
            {/* Chat Header */}
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">
                        {selectedChatData.avatar || selectedChatData.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    {selectedChatData.type === 'direct' && (
                      <div className={`absolute -bottom-1 -right-1 w-3 h-3 ${getStatusColor(getContactInfo(selectedChatData.participants[1])?.status || 'offline')} rounded-full border-2 border-white dark:border-gray-900`}></div>
                    )}
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {selectedChatData.name}
                    </h3>
                    {selectedChatData.type === 'direct' && (
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {getContactInfo(selectedChatData.participants[1])?.status === 'online' 
                          ? 'En línea' 
                          : `Última vez: ${getContactInfo(selectedChatData.participants[1])?.lastSeen}`}
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    <HiOutlinePhone className="w-5 h-5" />
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    <HiOutlineVideoCamera className="w-5 h-5" />
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    <HiOutlineDotsHorizontal className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatMessages.map((msg) => {
                const isOwn = msg.senderId === 'current-user'
                const contact = getContactInfo(msg.senderId)

                return (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex items-end space-x-2 max-w-xs lg:max-w-md ${isOwn ? 'flex-row-reverse space-x-reverse' : ''}`}>
                      {!isOwn && (
                        <div className="w-8 h-8 bg-gradient-to-r from-gray-400 to-gray-600 rounded-full flex items-center justify-center">
                          <span className="text-white text-xs font-semibold">
                            {contact?.avatar || msg.senderId[0]}
                          </span>
                        </div>
                      )}

                      <div className={`px-4 py-2 rounded-2xl ${
                        isOwn 
                          ? 'bg-blue-500 text-white rounded-br-md' 
                          : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-bl-md border border-gray-200 dark:border-gray-700'
                      }`}>
                        <p className="text-sm">{msg.content}</p>
                        <div className={`flex items-center justify-between mt-1 ${isOwn ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'}`}>
                          <span className="text-xs">{formatTime(msg.timestamp)}</span>
                          {isOwn && (
                            <div className="ml-2">
                              {msg.status === 'sent' && <HiOutlineCheck className="w-3 h-3" />}
                              {msg.status === 'delivered' && <HiOutlineCheckCircle className="w-3 h-3" />}
                              {msg.status === 'read' && <HiOutlineCheckCircle className="w-3 h-3 text-blue-200" />}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-t border-gray-200/50 dark:border-gray-700/50 p-4">
              <div className="flex items-end space-x-2">
                {/* Attachments */}
                <div className="relative">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setShowAttachments(!showAttachments)}
                    className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                  >
                    <HiOutlinePaperClip className="w-5 h-5" />
                  </motion.button>

                  <AnimatePresence>
                    {showAttachments && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8, y: 10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.8, y: 10 }}
                        className="absolute bottom-full left-0 mb-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-2"
                      >
                        <div className="flex flex-col space-y-1">
                          <button className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                            <HiOutlinePhotograph className="w-4 h-4 text-green-500" />
                            <span>Imagen</span>
                          </button>
                          <button className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                            <HiOutlineDocument className="w-4 h-4 text-blue-500" />
                            <span>Archivo</span>
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Message Input */}
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Escribe un mensaje..."
                    className="w-full px-4 py-3 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
                  />

                  {/* Emoji Button */}
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                      className="p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                    >
                      <HiOutlineEmojiHappy className="w-5 h-5" />
                    </motion.button>

                    <AnimatePresence>
                      {showEmojiPicker && (
                        <motion.div
                          initial={{ opacity: 0, scale: 0.8, y: 10 }}
                          animate={{ opacity: 1, scale: 1, y: 0 }}
                          exit={{ opacity: 0, scale: 0.8, y: 10 }}
                          className="absolute bottom-full right-0 mb-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-3"
                        >
                          <div className="grid grid-cols-6 gap-2">
                            {emojis.map((emoji) => (
                              <button
                                key={emoji}
                                onClick={() => {
                                  setMessage(prev => prev + emoji)
                                  setShowEmojiPicker(false)
                                }}
                                className="text-lg hover:bg-gray-100 dark:hover:bg-gray-700 rounded p-1 transition-colors"
                              >
                                {emoji}
                              </button>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>

                {/* Send Button */}
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={sendMessage}
                  disabled={!message.trim()}
                  className="p-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 dark:disabled:bg-gray-700 text-white rounded-2xl transition-colors disabled:cursor-not-allowed"
                >
                  <HiOutlinePaperAirplane className="w-5 h-5" />
                </motion.button>
              </div>
            </div>
          </>
        ) : (
          /* No chat selected */
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <HiOutlineChatAlt2 className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Selecciona una conversación
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                Elige una conversación para empezar a chatear
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}