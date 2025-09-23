import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useToast } from '../context/ToastContext'
import {
  HiOutlineShoppingBag,
  HiOutlineStar,
  HiOutlineHeart,
  HiOutlineShoppingCart,
  HiOutlineFilter,
  HiOutlineSearch,
  HiOutlineTrendingUp,
  HiOutlineGift,
  HiOutlineLightningBolt,
  HiOutlineBadgeCheck,
  HiOutlineColorSwatch,
  HiOutlineBookOpen,
  HiOutlineMoon,
  HiOutlineMusicNote,
  HiOutlineTag,
  HiOutlineUser,
  HiOutlineCamera,
  HiOutlineSparkles,
  HiOutlineBeaker,
  HiOutlineCash,
  HiOutlineCode,
  HiOutlineEye,
  HiOutlineX
} from 'react-icons/hi'
import Layout from '../components/layout/Layout';

export default function TiendaPage() {
  // ...todo el código y hooks previos...

  const getRarityName = (rarity: string) => {
    const names = {
      common: 'Común',
      rare: 'Raro',
      epic: 'Épico',
      legendary: 'Legendario',
      mythic: 'Mítico'
    }
    return names[rarity as keyof typeof names] || 'Común'
  }

  return (
    <Layout>
      {/* ...todo el contenido original de la página, como estaba antes... */}
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50/30 to-indigo-50/50 dark:from-gray-900 dark:via-purple-950/30 dark:to-blue-950/30">
        {/* Header */}
        {/* ...resto del contenido sin cambios... */}
      </div>
    </Layout>
  )
}