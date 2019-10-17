# frozen_string_literal: true

require 'awspec'
Awsecrets.load(secrets_path: File.expand_path('./secrets.yml', File.dirname(__FILE__)))

describe ecr_repository('kaos-2-test-backend') do
  it { should exist }
  its(:repository_name) { should eq 'kaos-2-test-backend' }

end