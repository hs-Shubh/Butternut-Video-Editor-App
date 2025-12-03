import React from 'react'
import { View, Text, Button } from 'react-native'
import Slider from '@react-native-community/slider'
import type { Overlay } from '../types'

type Props = {
  overlay: Overlay
  onChange: (o: Overlay) => void
  onRemove: () => void
}

export default function OverlayControls({ overlay, onChange, onRemove }: Props) {
  return (
    <View style={{ padding: 8 }}>
      <Text>Scale</Text>
      <Slider
        minimumValue={0.1}
        maximumValue={3}
        value={overlay.scale}
        onValueChange={(v) => onChange({ ...overlay, scale: v })}
      />
      <Text>Rotation</Text>
      <Slider
        minimumValue={-180}
        maximumValue={180}
        value={overlay.rotation}
        onValueChange={(v) => onChange({ ...overlay, rotation: v })}
      />
      <Text>Opacity</Text>
      <Slider
        minimumValue={0}
        maximumValue={1}
        value={overlay.opacity}
        onValueChange={(v) => onChange({ ...overlay, opacity: v })}
      />
      <Button title="Remove" onPress={onRemove} />
    </View>
  )
}
