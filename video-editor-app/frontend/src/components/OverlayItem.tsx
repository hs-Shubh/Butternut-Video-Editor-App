import React from 'react'
import { View, Text, Image } from 'react-native'
import { Video } from 'expo-av'
import type { Overlay } from '../types'

type Props = {
  overlay: Overlay
  currentTime: number
  resolution: { width: number; height: number }
  selected?: boolean
  onSelect?: (id: string) => void
}

export default function OverlayItem({ overlay, currentTime, resolution, selected, onSelect }: Props) {
  const visible = currentTime >= overlay.start_time && currentTime <= overlay.end_time
  if (!visible) return null
  const x = overlay.position.x * resolution.width
  const y = overlay.position.y * resolution.height
  const size = 100 * overlay.scale
  const assets: Record<string, any> = {
    'overlay_image.png': require('../../assets/overlay_image.png'),
    'overlay_clip.mp4': require('../../assets/overlay_clip.mp4'),
  }
  const commonStyle = {
    position: 'absolute' as const,
    left: x,
    top: y,
    opacity: overlay.opacity,
    transform: [{ rotate: `${overlay.rotation}deg` }],
    zIndex: overlay.z_index,
  }
  if (overlay.type === 'text') {
    return (
      <View style={[commonStyle, selected ? { borderWidth: 1, borderColor: '#4ade80' } : null]} onTouchStart={() => onSelect && onSelect(overlay.id)}> 
        <Text
          style={{
            fontSize: overlay.font_size || 24,
            color: 'white',
            backgroundColor: overlay.background_box ? 'rgba(0,0,0,0.5)' : 'transparent',
            paddingHorizontal: 8,
            paddingVertical: 4,
          }}
        >
          {overlay.content}
        </Text>
      </View>
    )
  }
  if (overlay.type === 'image') {
    return (
      <Image
        source={assets[overlay.content] ? assets[overlay.content] : { uri: overlay.content }}
        style={[commonStyle, { width: size, height: size }, selected ? { borderWidth: 1, borderColor: '#4ade80' } : null]}
        onTouchStart={() => onSelect && onSelect(overlay.id)}
      />
    )
  }
  return (
    <Video
      source={assets[overlay.content] ? assets[overlay.content] : { uri: overlay.content }}
      style={[commonStyle, { width: size, height: size }]}
      shouldPlay
      isLooping
      resizeMode="cover"
      onTouchStart={() => onSelect && onSelect(overlay.id)}
    />
  )
}
