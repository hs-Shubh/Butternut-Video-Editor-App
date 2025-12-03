import React from 'react'
import { View } from 'react-native'
import type { Overlay } from '../types'

type Props = {
  overlays: Overlay[]
  duration: number
}

export default function Timeline({ overlays, duration }: Props) {
  return (
    <View style={{ height: 60, backgroundColor: '#111', padding: 8 }}>
      {overlays.map((o) => {
        const left = (o.start_time / duration) * 100
        const width = ((o.end_time - o.start_time) / duration) * 100
        return (
          <View
            key={o.id}
            style={{
              position: 'absolute',
              left: `${left}%`,
              width: `${width}%`,
              height: 40,
              backgroundColor: '#4ade80',
              borderRadius: 6,
              opacity: 0.8,
            }}
          />
        )
      })}
    </View>
  )
}
