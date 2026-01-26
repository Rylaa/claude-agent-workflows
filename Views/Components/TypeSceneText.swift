import SwiftUI

/// TypeSceneText component from Figma design
/// File: bt65gbJ6sSdKRP4x3IY151, Node: 10203:16369
/// Features: Angular gradient text, semi-transparent borders
@available(iOS 15.0, *)
struct TypeSceneText: View {
    var body: some View {
        ZStack {
            // Background with radial gradient overlay
            ZStack {
                Color(hex: "#150200")

                RadialGradient(
                    gradient: Gradient(stops: [
                        .init(color: Color(hex: "#f02912"), location: 0.0),
                        .init(color: Color(hex: "#150200"), location: 1.0)
                    ]),
                    center: .center,
                    startRadius: 0,
                    endRadius: 200
                )
                .opacity(0.2)
            }

            VStack(spacing: 16) {
                // Header area (placeholder for actual header content)
                HStack(spacing: 8) {
                    Text("Create")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(.white)

                    Spacer()

                    HStack(spacing: 8) {
                        Image(systemName: "star.fill")
                            .foregroundColor(Color(hex: "#ffd100"))

                        Text("10")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                    }
                }
                .frame(height: 32)
                .padding(.horizontal, 16)

                Spacer()

                // Main content area with gradient text
                VStack(spacing: 12) {
                    // Border with semi-transparent white stroke (opacity: 0.4)
                    RoundedRectangle(cornerRadius: 24)
                        .stroke(Color.white.opacity(0.4), lineWidth: 1.0)
                        .frame(height: 120)
                        .overlay(
                            // Gradient text inside border
                            Text("Type a scene to generate your video")
                                .font(.system(size: 14, weight: .regular))
                                .multilineTextAlignment(.center)
                                .foregroundStyle(
                                    AngularGradient(
                                        stops: [
                                            Gradient.Stop(color: Color(hex: "#bc82f3"), location: 0.1673),
                                            Gradient.Stop(color: Color(hex: "#f4b9ea"), location: 0.2365),
                                            Gradient.Stop(color: Color(hex: "#8d98ff"), location: 0.3518),
                                            Gradient.Stop(color: Color(hex: "#aa6eee"), location: 0.5815),
                                            Gradient.Stop(color: Color(hex: "#ff6777"), location: 0.697),
                                            Gradient.Stop(color: Color(hex: "#ffba71"), location: 0.8095),
                                            Gradient.Stop(color: Color(hex: "#c686ff"), location: 0.9241)
                                        ],
                                        center: .center
                                    )
                                )
                                .padding(.horizontal, 20)
                        )

                    // Options row
                    HStack(spacing: 16) {
                        OptionButton(text: "Image to Video")
                        OptionButton(text: "Veo 3")
                        OptionButton(text: "5s")
                        OptionButton(text: "720P")
                    }
                    .padding(.horizontal, 16)
                }
                .padding(.bottom, 40)
            }
            .padding(.top, 60)
        }
        .frame(width: 390, height: 844)
        .cornerRadius(50.0)
        .clipped()
    }
}

/// Helper view for option buttons
@available(iOS 15.0, *)
struct OptionButton: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.system(size: 14, weight: .medium))
            .foregroundColor(.white)
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.white.opacity(0.1))
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.white.opacity(0.2), lineWidth: 0.7)
                    )
            )
    }
}

/// Color extension to support hex color strings
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

#Preview {
    if #available(iOS 15.0, *) {
        TypeSceneText()
    } else {
        Text("iOS 15.0+ required for AngularGradient")
    }
}
