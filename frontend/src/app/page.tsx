import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <nav className="mb-12 flex justify-end gap-5 text-sm font-semibold text-white">
          <Link href="/jobs" className="hover:text-blue-200">Browse Jobs</Link>
          <Link href="/login" className="hover:text-blue-200">Sign In</Link>
          <Link href="/register" className="hover:text-blue-200">Create Account</Link>
        </nav>
        <div className="text-center text-white">
          <div className="inline-block mb-6 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20">
            <span className="text-sm font-medium">🚀 Ethiopia's #1 AI-Powered Career Platform</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
            Find Your Dream Job with AI
          </h1>
          <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto leading-relaxed">
            Upload your CV and let our intelligent AI system analyze your skills, experience, and qualifications 
            to match you with the perfect job opportunities in Ethiopia and beyond.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/register"
              className="bg-white text-indigo-700 px-8 py-4 rounded-lg font-semibold hover:bg-blue-50 transition shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              Get Started Free
            </Link>
            <Link
              href="/jobs"
              className="bg-indigo-500/30 backdrop-blur-sm text-white px-8 py-4 rounded-lg font-semibold hover:bg-indigo-500/50 transition border border-white/30"
            >
              Browse Jobs
            </Link>
            <Link
              href="/login"
              className="bg-white/10 backdrop-blur-sm text-white px-8 py-4 rounded-lg font-semibold hover:bg-white/20 transition border border-white/30"
            >
              Sign In
            </Link>
          </div>
          <div className="mt-8 flex justify-center gap-8 text-sm text-blue-200">
            <div className="flex items-center gap-2">
              <span className="text-2xl">✓</span>
              <span>Free to use</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">✓</span>
              <span>AI-powered matching</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">✓</span>
              <span>Real-time job alerts</span>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="bg-white/10 backdrop-blur-sm p-8 rounded-2xl border border-white/20 hover:bg-white/20 transition">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-3 text-white">AI-Powered Matching</h3>
            <p className="text-blue-100 leading-relaxed">
              Our advanced AI analyzes your CV using semantic understanding and matches you with jobs 
              that truly fit your skills, experience, and career goals.
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm p-8 rounded-2xl border border-white/20 hover:bg-white/20 transition">
            <div className="text-4xl mb-4">📄</div>
            <h3 className="text-xl font-semibold mb-3 text-white">Smart CV Analysis</h3>
            <p className="text-blue-100 leading-relaxed">
              Upload your CV and let our system automatically extract your skills, experience, 
              certifications, and qualifications with 95%+ accuracy.
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-sm p-8 rounded-2xl border border-white/20 hover:bg-white/20 transition">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-3 text-white">Personalized Recommendations</h3>
            <p className="text-blue-100 leading-relaxed">
              Get job recommendations tailored to your profile, career level, and field of expertise 
              with explanations for why each job is a good match.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="mt-24 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">How It Works</h2>
          <p className="text-blue-200 mb-12 max-w-2xl mx-auto">
            Get hired in 4 simple steps with our intelligent platform
          </p>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
              <div className="bg-white text-indigo-700 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-xl">1</div>
              <h3 className="font-semibold mb-2 text-lg">Create Account</h3>
              <p className="text-blue-200 text-sm">Sign up in 30 seconds</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
              <div className="bg-white text-indigo-700 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-xl">2</div>
              <h3 className="font-semibold mb-2 text-lg">Upload CV</h3>
              <p className="text-blue-200 text-sm">AI analyzes your skills</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
              <div className="bg-white text-indigo-700 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-xl">3</div>
              <h3 className="font-semibold mb-2 text-lg">Get Matches</h3>
              <p className="text-blue-200 text-sm">Receive personalized jobs</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
              <div className="bg-white text-indigo-700 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-xl">4</div>
              <h3 className="font-semibold mb-2 text-lg">Apply & Get Hired</h3>
              <p className="text-blue-200 text-sm">One-click apply to jobs</p>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-24 grid md:grid-cols-3 gap-8 text-center text-white">
          <div>
            <div className="text-4xl font-bold mb-2">500+</div>
            <div className="text-blue-200">Active Jobs</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">50+</div>
            <div className="text-blue-200">Companies</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">1000+</div>
            <div className="text-blue-200">Job Seekers</div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-24 text-center">
          <div className="bg-white/10 backdrop-blur-sm p-12 rounded-2xl border border-white/20">
            <h2 className="text-3xl font-bold mb-4 text-white">Ready to Find Your Dream Job?</h2>
            <p className="text-blue-200 mb-8 max-w-2xl mx-auto">
              Join thousands of job seekers who have found their perfect career match through our AI-powered platform.
            </p>
            <Link
              href="/register"
              className="inline-block bg-white text-indigo-700 px-8 py-4 rounded-lg font-semibold hover:bg-blue-50 transition shadow-lg hover:shadow-xl transform hover:-translate-y-1"
            >
              Create Free Account
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-20 border-t border-white/20 py-8 text-center text-blue-200 text-sm">
        <p>© 2024 AI Job Matching Ethiopia. All rights reserved.</p>
      </footer>
    </div>
  );
}
