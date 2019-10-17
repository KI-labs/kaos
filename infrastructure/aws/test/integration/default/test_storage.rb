# frozen_string_literal: true

require 'awspec'
require 'aws-sdk'
require 'rhcl'

s3_name = 'kaos-2-test'
# Load the terraform state file and convert it into a Ruby hash
state_file = 'terraform.tfstate.d/kitchen-terraform-default-aws/terraform.tfstate'
tf_state = JSON.parse(File.open(state_file).read)
tf_state['modules'].each do |val|
 if val['path'].length == 2
    if val['path'][1] == 'storage'
        ENV['AWS_REGION'] = val['outputs']['region']['value']
    end
 end
end


# Test the Storage resource
describe s3_bucket(s3_name.to_s) do
  it { should exist }
  it { should have_tag('project').value('kaos') }
  it { should have_tag('env').value('test') }
  it { should have_tag('version').value('2') }
  it { should have_versioning_enabled }
end