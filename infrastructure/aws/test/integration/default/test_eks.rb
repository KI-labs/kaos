# frozen_string_literal: true

require 'awspec'
Awsecrets.load(secrets_path: File.expand_path('./secrets.yml', File.dirname(__FILE__)))

# this does not work
describe eks('kaos-2-test-eks-cluster') do
    it { should exist }
end