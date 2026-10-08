pragma Singleton
import QtQuick 2.15

QtObject {
    id: theme
    
    // Color tokens (from UI/UX document)
    readonly property QtObject colors: QtObject {
        // Background colors
        readonly property color bgDeep: "#05070F"
        readonly property color bgSpace: "#0A1230"
        readonly property color bgSpaceEnd: "#03050B"
        
        // Panel colors
        readonly property color panelFill: "#1A283280"  // rgba(10, 18, 40, 0.72) but more opaque
        readonly property color panelBorder: "#3C8CFF8C"  // rgba(60, 140, 255, 0.55)
        readonly property color panelGlow: "#2E8BFF59"   // Panel glow effect
        
        // Accent colors
        readonly property color accentBlue: "#2E8BFF"
        readonly property color accentCyan: "#27E0FF" 
        readonly property color accentViolet: "#7B5CFF"
        
        // Status colors
        readonly property color okGreen: "#2EE66B"
        readonly property color warnAmber: "#FFC247"
        readonly property color infoBlue: "#4DA3FF"
        readonly property color danger: "#FF4D6A"
        
        // Text colors
        readonly property color textPrimary: "#EAF2FF"
        readonly property color textSecondary: "#8FA3C7"
        readonly property color textTertiary: "#5A6B8A"
        
        // Interactive states
        readonly property color buttonHover: "#3C8CFF"
        readonly property color buttonActive: "#1D5FD6"
        readonly property color inputBg: "#0F1728"
        readonly property color inputBorder: "#2A3B5F"
        readonly property color inputFocus: "#2E8BFF"
    }
    
    // Typography
    readonly property QtObject fonts: QtObject {
        readonly property string primary: "Inter"
        readonly property string mono: "JetBrains Mono"
        
        // Font sizes
        readonly property int tiny: 10
        readonly property int small: 11
        readonly property int body: 13
        readonly property int panelTitle: 14
        readonly property int navTitle: 15
        readonly property int heading: 22
        readonly property int large: 28
    }
    
    // Spacing scale
    readonly property QtObject spacing: QtObject {
        readonly property int xs: 4
        readonly property int sm: 8
        readonly property int md: 12
        readonly property int lg: 16
        readonly property int xl: 24
        readonly property int xxl: 32
    }
    
    // Effects
    readonly property QtObject effects: QtObject {
        readonly property int panelRadius: 8
        readonly property int buttonRadius: 6
        readonly property int glowRadius: 12
        readonly property real panelOpacity: 0.95
        readonly property int animationDuration: 200
    }
    
    // Avatar colors
    readonly property QtObject avatar: QtObject {
        readonly property color hairColor: "#C8B2E8"  // Silver-lavender
        readonly property color eyeGlow: accentBlue
        readonly property color gemColor: accentCyan
        readonly property color haloColor: accentBlue
        readonly property color orbColor: accentCyan
        readonly property color ringColor: accentViolet
    }
    
    // Widget specific colors
    readonly property QtObject widgets: QtObject {
        // Progress bars
        readonly property color progressTrack: "#FFFFFF1F"  // rgba(255,255,255,0.12)
        readonly property color progressFill: accentCyan
        readonly property color progressSuccess: okGreen
        readonly property color progressWarning: warnAmber
        readonly property color progressError: danger
        
        // Sparklines
        readonly property color sparkline: accentCyan
        readonly property color sparklineGlow: "#27E0FF33"
        
        // System status
        readonly property color cpuColor: accentBlue
        readonly property color memoryColor: accentCyan
        readonly property color gpuColor: accentViolet
        readonly property color networkColor: okGreen
    }
}