import React, { useEffect, useRef, useState } from 'react'
import { View, Text, Button, TouchableOpacity, PanResponder } from 'react-native'
import { Video } from 'expo-av'
import * as DocumentPicker from 'expo-document-picker'
import type { Overlay, Metadata, Position } from '../types'
import OverlayItem from '../components/OverlayItem'
import Timeline from '../components/Timeline'
import OverlayControls from '../components/OverlayControls'
import { uploadEdit, getStatus, resultUrl } from '../api/client'

const sampleOverlays: Overlay[] = [
  {
    id: 'overlay-text-1',
    type: 'text',
    content: 'Happy New Year!',
    position: { x: 0.25, y: 0.8 },
    scale: 1.0,
    rotation: 0,
    opacity: 0.95,
    start_time: 2.5,
    end_time: 6.0,
    z_index: 2,
    font_size: 32,
    background_box: true,
  },
  {
    id: 'overlay-image-1',
    type: 'image',
    content: 'https://drive.google.com/uc?export=view&id=overlay_image_id',
    position: { x: 0.1, y: 0.1 },
    scale: 1.2,
    rotation: -10,
    opacity: 0.9,
    start_time: 1.0,
    end_time: 4.0,
    z_index: 3,
  },
  {
    id: 'overlay-video-1',
    type: 'video',
    content: 'https://drive.google.com/uc?export=download&id=overlay_clip_id',
    position: { x: 0.6, y: 0.2 },
    scale: 0.8,
    rotation: 0,
    opacity: 1.0,
    start_time: 3.0,
    end_time: 8.0,
    z_index: 4,
  },
]

export default function VideoEditorScreen() {
  const [videoUri, setVideoUri] = useState<string | null>(null)
  const [overlays, setOverlays] = useState<Overlay[]>(sampleOverlays)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(10)
  const [outputRes, setOutputRes] = useState<{ width: number; height: number }>({ width: 1280, height: 720 })
  const [jobId, setJobId] = useState<string | null>(null)
  const [progress, setProgress] = useState<number>(0)
  const player = useRef<Video>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  useEffect(() => {
    const interval = setInterval(async () => {
      const status = await player.current?.getStatusAsync()
      if (status && 'positionMillis' in status && 'durationMillis' in status) {
        setCurrentTime((status.positionMillis || 0) / 1000)
        setDuration(((status.durationMillis as number) || 10000) / 1000)
      }
    }, 300)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    let t: any
    if (jobId) {
      t = setInterval(async () => {
        try {
          const s = await getStatus(jobId)
          setProgress(s.progress_percent)
        } catch {}
      }, 1500)
    }
    return () => clearInterval(t)
  }, [jobId])

  const addText = () => {
    const id = `text-${Date.now()}`
    setOverlays([
      ...overlays,
      {
        id,
        type: 'text',
        content: 'New Text',
        position: { x: 0.5, y: 0.5 },
        scale: 1,
        rotation: 0,
        opacity: 1,
        start_time: 0,
        end_time: 5,
        z_index: overlays.length + 1,
        font_size: 28,
        background_box: false,
      },
    ])
  }

  const addImage = () => {
    const id = `img-${Date.now()}`
    setOverlays([
      ...overlays,
      {
        id,
        type: 'image',
        content: 'overlay_image.png',
        position: { x: 0.2, y: 0.2 },
        scale: 1,
        rotation: 0,
        opacity: 1,
        start_time: 1,
        end_time: 7,
        z_index: overlays.length + 1,
      },
    ])
  }

  const addClip = () => {
    const id = `vid-${Date.now()}`
    setOverlays([
      ...overlays,
      {
        id,
        type: 'video',
        content: 'overlay_clip.mp4',
        position: { x: 0.7, y: 0.3 },
        scale: 0.7,
        rotation: 0,
        opacity: 1,
        start_time: 2,
        end_time: 8,
        z_index: overlays.length + 1,
      },
    ])
  }

  const pickVideo = async () => {
    const res = await DocumentPicker.getDocumentAsync({ type: 'video/*' })
    if (res.assets && res.assets.length > 0) {
      setVideoUri(res.assets[0].uri)
    }
  }

  const submit = async () => {
    if (!videoUri) return
    const meta: Metadata = {
      title: 'My Edit',
      overlays: overlays,
      output_format: 'mp4',
      resolution: outputRes,
    }
    const r = await uploadEdit(videoUri, meta)
    setJobId(r.job_id)
  }

  const resolution = { width: 320, height: 180 }
  const sorted = [...overlays].sort((a, b) => a.z_index - b.z_index)

  const pan = PanResponder.create({
    onMoveShouldSetPanResponder: () => !!selectedId,
    onPanResponderMove: (_, gestureState) => {
      if (!selectedId) return
      const x = gestureState.moveX
      const y = gestureState.moveY
      const nx = Math.max(0, Math.min(1, x / resolution.width))
      const ny = Math.max(0, Math.min(1, y / resolution.height))
      setOverlays((prev) => prev.map((o) => (o.id === selectedId ? { ...o, position: { x: nx, y: ny } } : o)))
    },
  })

  return (
    <View style={{ flex: 1, backgroundColor: '#000' }}>
      <View style={{ padding: 12, flexDirection: 'row', gap: 8 }}>
        <Button title="Pick Video" onPress={pickVideo} />
        <Button title="Add Text" onPress={addText} />
        <Button title="Add Image" onPress={addImage} />
        <Button title="Add Clip" onPress={addClip} />
        <Button title="Preset 720p" onPress={() => setOutputRes({ width: 1280, height: 720 })} />
        <Button title="Preset 1080p" onPress={() => setOutputRes({ width: 1920, height: 1080 })} />
      </View>
      <View style={{ alignItems: 'center' }}>
        {videoUri ? (
          <Video
            ref={player}
            source={{ uri: videoUri }}
            style={{ width: resolution.width, height: resolution.height, backgroundColor: '#222' }}
            resizeMode="contain"
            shouldPlay
            isLooping
          />
        ) : (
          <Text style={{ color: 'white' }}>Select a video to preview</Text>
        )}
        <View style={{ position: 'absolute', width: resolution.width, height: resolution.height }} {...pan.panHandlers}>
          {sorted.map((o) => (
            <OverlayItem key={o.id} overlay={o} currentTime={currentTime} resolution={resolution} selected={selectedId === o.id} onSelect={(id) => setSelectedId(id)} />
          ))}
        </View>
      </View>
      <Timeline overlays={sorted} duration={duration || 10} />
      <View style={{ padding: 12, flexDirection: 'row', gap: 8 }}>
        <Button title="Submit" onPress={submit} />
        {jobId && <Text style={{ color: 'white' }}>Progress: {progress}%</Text>}
        {jobId && progress === 100 && (
          <TouchableOpacity onPress={() => {}}>
            <Text style={{ color: '#4ade80' }}>Result: {resultUrl(jobId)}</Text>
          </TouchableOpacity>
        )}
      </View>
      {sorted[0] && (
        <OverlayControls
          overlay={sorted[sorted.length - 1]}
          onChange={(o) => setOverlays(overlays.map((x) => (x.id === o.id ? o : x)))}
          onRemove={() => setOverlays(overlays.slice(0, overlays.length - 1))}
        />
      )}
    </View>
  )
}
