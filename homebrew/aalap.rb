class Aalap < Formula
  include Language::Python::Virtualenv

  desc "Interactive CLI for Claude AI with MCP server support"
  homepage "https://github.com/caltycs/aalap"
  url "https://github.com/caltycs/aalap/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "YOUR_SHA256_HERE"
  license "Apache"

  depends_on "python@3.11"

  resource "anthropic" do
    url "https://files.pythonhosted.org/packages/source/a/anthropic/anthropic-0.40.0.tar.gz"
    sha256 "ANTHROPIC_SHA256_HERE"
  end

  def install
    virtualenv_install_with_resources
  end

  def caveats
    <<~EOS
      Aalap has been installed!

      To get started:
        1. Set your Anthropic API key:
           aalap config --api-key YOUR_API_KEY

        2. Launch Aalap:
           aalap

      Configuration is stored in ~/.aalap/

      For more information, visit: https://github.com/caltycs/aalap
    EOS
  end

  test do
    system "#{bin}/aalap", "--help"
  end
end