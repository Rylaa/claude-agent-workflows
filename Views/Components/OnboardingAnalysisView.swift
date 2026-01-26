import SwiftUI

/// OnboardingAnalysisView - Personalized analysis onboarding screen for ViralZ
/// Figma File: ElHzcNWC8pSYTz2lhPP9h0, Node: 6:46
/// Features: Progress indicator, highlighted title, decorative visual, profile selector, trust badges, CTA
@available(iOS 15.0, *)
struct OnboardingAnalysisView: View {
    // MARK: - Properties

    /// Current step in the onboarding flow (1-6)
    let currentStep: Int

    /// Username input binding
    @Binding var usernameInput: String

    /// Selected profile name
    let selectedProfile: String

    /// Selected profile username
    let selectedUsername: String

    /// Action when analyze button is tapped
    let onAnalyzeTapped: () -> Void

    /// Action when profile selector is tapped
    let onProfileSelectorTapped: () -> Void

    // MARK: - Constants

    private let totalSteps = 6

    // MARK: - Body

    var body: some View {
        ZStack {
            // Layer 1: Background (zIndex: 100)
            Color.black
                .ignoresSafeArea()

            // Layer 2: Decorative Visual Section (zIndex: 200)
            decorativeVisualSection

            // Layer 3 & 4: Floating Action Buttons (zIndex: 300, 350)
            floatingActionButtons

            // Layer 5: Content Stack (zIndex: 400)
            contentStack
        }
        .frame(width: 390, height: 844)
        .clipped()
    }

    // MARK: - Decorative Visual Section

    private var decorativeVisualSection: some View {
        Image("DecorativeVisual")
            .resizable()
            .scaledToFit()
            .frame(width: 300, height: 300)
            .blur(radius: 4)
            .offset(y: 180 - 422) // absoluteY: 180, center of screen at 422
            .accessibilityHidden(true)
    }

    // MARK: - Floating Action Buttons

    private var floatingActionButtons: some View {
        ZStack {
            // Left button - Chart icon (zIndex: 300, absoluteY: 400)
            Image("IconChart")
                .resizable()
                .scaledToFit()
                .frame(width: 49, height: 62)
                .offset(x: -120, y: 400 - 422)
                .accessibilityLabel("Analytics chart")

            // Right button - Sparkle icon (zIndex: 350, absoluteY: 320)
            Image("IconSparkle")
                .resizable()
                .scaledToFit()
                .frame(width: 49, height: 62)
                .offset(x: 120, y: 320 - 422)
                .accessibilityLabel("AI sparkle")
        }
    }

    // MARK: - Content Stack

    private var contentStack: some View {
        VStack(spacing: 0) {
            // Progress Indicator
            progressIndicator
                .padding(.top, 60)
                .padding(.bottom, 24)

            // Header Section
            headerSection
                .padding(.bottom, 200) // Space for decorative visual

            // Username Input Section
            usernameInputSection
                .padding(.horizontal, 24)
                .padding(.bottom, 24)

            // Trust Badges
            trustBadges
                .padding(.bottom, 24)

            // CTA Button
            ctaButton
                .padding(.horizontal, 24)

            Spacer()
        }
    }

    // MARK: - Progress Indicator

    private var progressIndicator: some View {
        HStack(spacing: 8) {
            ForEach(1...totalSteps, id: \.self) { step in
                Circle()
                    .fill(step == currentStep ? Color(hex: "#f2f20d") : Color(hex: "#858585"))
                    .frame(width: 8, height: 8)
            }
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Step \(currentStep) of \(totalSteps)")
    }

    // MARK: - Header Section

    private var headerSection: some View {
        VStack(spacing: 24) {
            // Title with highlighted "personalized"
            titleText

            // Description
            Text("Connect your TikTok account to get personalized insights and recommendations.")
                .font(.custom("Poppins", size: 16))
                .fontWeight(.regular)
                .lineSpacing(8)
                .multilineTextAlignment(.center)
                .foregroundColor(.white)
                .padding(.horizontal, 24)
        }
    }

    private var titleText: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack(spacing: 0) {
                Text("Ready for your ")
                    .font(.custom("Poppins", size: 24))
                    .fontWeight(.semibold)
                    .foregroundColor(.white)
                Text("personalized")
                    .font(.custom("Poppins", size: 24))
                    .fontWeight(.semibold)
                    .foregroundColor(Color(hex: "#f2f20d"))
            }
            Text("analysis?")
                .font(.custom("Poppins", size: 24))
                .fontWeight(.semibold)
                .foregroundColor(.white)
        }
        .multilineTextAlignment(.center)
        .lineSpacing(12)
        .padding(.horizontal, 24)
        .accessibilityLabel("Ready for your personalized analysis?")
    }

    // MARK: - Username Input Section

    private var usernameInputSection: some View {
        VStack(spacing: 12) {
            // Profile Selector
            profileSelector

            // Text Input Field
            textInputField
        }
    }

    private var profileSelector: some View {
        Button(action: onProfileSelectorTapped) {
            HStack {
                // Profile Preview
                HStack(spacing: 8) {
                    Image("ProfileViralz")
                        .resizable()
                        .scaledToFill()
                        .frame(width: 32, height: 32)
                        .clipShape(Circle())

                    VStack(alignment: .leading, spacing: 2) {
                        Text(selectedProfile)
                            .font(.custom("Poppins", size: 11.8))
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                            .lineLimit(1)

                        Text(selectedUsername)
                            .font(.custom("Poppins", size: 10.1))
                            .fontWeight(.regular)
                            .foregroundColor(Color(hex: "#858585"))
                            .lineLimit(1)
                    }
                }

                Spacer()

                // Dropdown Chevron
                Image("IconChevronDown")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 12, height: 12)
                    .foregroundColor(.white)
            }
            .padding(12)
            .background(Color.clear)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color(hex: "#1e1e1e"), lineWidth: 1)
            )
        }
        .accessibilityLabel("Select profile, currently \(selectedProfile)")
        .accessibilityHint("Double tap to change profile")
    }

    private var textInputField: some View {
        HStack(spacing: 10) {
            Text("@")
                .font(.custom("Poppins", size: 14))
                .fontWeight(.regular)
                .foregroundColor(.white)

            TextField("e.g. viralz", text: $usernameInput)
                .font(.custom("Poppins", size: 14))
                .fontWeight(.regular)
                .foregroundColor(.white)
                .autocapitalization(.none)
                .disableAutocorrection(true)
        }
        .padding(.leading, 16)
        .padding(.vertical, 12)
        .background(Color.clear)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(
                    LinearGradient(
                        stops: [
                            .init(color: Color(hex: "#1e1e1e").opacity(0), location: 0),
                            .init(color: Color(hex: "#1e1e1e"), location: 1)
                        ],
                        startPoint: .leading,
                        endPoint: .trailing
                    ),
                    lineWidth: 1
                )
        )
        .accessibilityLabel("TikTok username")
        .accessibilityHint("Enter your TikTok username without the @ symbol")
    }

    // MARK: - Trust Badges

    private var trustBadges: some View {
        HStack(spacing: 12) {
            // Safe & Secure Badge
            trustBadge(icon: "IconLock", text: "Safe & Secure")

            // Official TikTok API Badge
            trustBadge(icon: "IconTikTok", text: "Official Tiktok API")
        }
    }

    private func trustBadge(icon: String, text: String) -> some View {
        HStack(spacing: 4) {
            Image(icon)
                .resizable()
                .scaledToFit()
                .frame(width: 16, height: 16)

            Text(text)
                .font(.custom("Poppins", size: 14))
                .fontWeight(.medium)
                .foregroundColor(Color(hex: "#f2f20d"))
        }
        .accessibilityElement(children: .combine)
    }

    // MARK: - CTA Button

    private var ctaButton: some View {
        Button(action: onAnalyzeTapped) {
            Text("Analyze my account")
                .font(.custom("Poppins", size: 20))
                .fontWeight(.semibold)
                .foregroundColor(.black)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 16)
        }
        .background(Color(hex: "#f2f20d"))
        .cornerRadius(9999)
        .accessibilityLabel("Analyze my account")
        .accessibilityHint("Double tap to start analyzing your TikTok account")
    }
}

// MARK: - Placeholder Modifier

extension View {
    func placeholder<Content: View>(
        when shouldShow: Bool,
        alignment: Alignment = .leading,
        @ViewBuilder placeholder: () -> Content
    ) -> some View {
        ZStack(alignment: alignment) {
            placeholder().opacity(shouldShow ? 1 : 0)
            self
        }
    }
}

// MARK: - Color Extension

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
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Preview

@available(iOS 15.0, *)
struct OnboardingAnalysisView_Previews: PreviewProvider {
    @State static var username = ""

    static var previews: some View {
        OnboardingAnalysisView(
            currentStep: 6,
            usernameInput: $username,
            selectedProfile: "viralz",
            selectedUsername: "@viralz",
            onAnalyzeTapped: { print("Analyze tapped") },
            onProfileSelectorTapped: { print("Profile selector tapped") }
        )
        .previewDisplayName("Onboarding Analysis - Step 6")
    }
}
