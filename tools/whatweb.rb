#!/usr/bin/env ruby

require 'json'
require "fileutils"
require "pathname"

if ARGV.size != 2 then
    puts("[*] Usage: #{$0} src_dir dst_dir")
    exit(0)
end

$src_plugin_dir = File.expand_path(ARGV[0])
$dst_plugin_dir = File.expand_path(ARGV[1])

def randstr
  1111111111111.to_s(36)
end

def rand(v)
  1111111111111
end


class Plugin
  def Plugin.define()
    yield if block_given?
  end
end

$plugin_matches = nil

def matches(value)
  new_value = Marshal.load( Marshal.dump(value))
  wrong_items = [[:path, :url], [:regxp, :regexp], [:regex, :regexp]]

  value.each_index do |index|
    value[index].each_key do |key|
      wrong_items.each_index do |wrong_index|
        if key == wrong_items[wrong_index][0]
          new_value[index][wrong_items[wrong_index][1]] = value[index][wrong_items[wrong_index][0]]
          new_value[index].delete(wrong_items[wrong_index][0])
        end
      end
    end

    if new_value[index][:version].nil? and new_value[index]["offset"].nil?
        new_value[index].delete(:offset)
        new_value[index].delete("offset")
    end

    [:version, :os, :string, :account, :model, :firmware, :module, :filepath].each do |label|
      if !value[index][label].nil? and value[index][label].class == Regexp
        new_value[index][:regexp] = value[index][label]
        if label == :version and new_value[index]["offset"].nil? and new_value[index][:offset].nil?
            new_value[index][:offset] = 1
        end
        new_value[index].delete(label)
      end
    end
  end

  $plugin_matches = new_value
end


$plugin_name = nil
def name(value)
  $plugin_name = value
end

$plugin_author = nil

def authors(value)
  $plugin_author = value.join(', ')
end

$plugin_version = nil

def version(value)
  $plugin_version = value
end

$plugin_description = nil

def description(value)
  $plugin_description = value
end

$plugin_website = nil

def website(value)
  $plugin_website = value
end

$plugin_cve = nil

def cve(value)
  $plugin_cve = value
end

$plugin_dorks = nil

def dorks(value)
  $plugin_dorks = value
end

def passive()
end

def aggressive()
end


if !File.exists?($dst_plugin_dir)
  FileUtils.mkdir_p($dst_plugin_dir)
end


Dir.foreach($src_plugin_dir) do |file|
  if file != "." and file != ".." and file.end_with?(".rb")
    $plugin_name = nil
    $plugin_author = nil
    $plugin_version = nil
    $plugin_description = nil
    $plugin_website = nil
    $plugin_matches = nil
    $plugin_cve = nil
    $plugin_dorks = nil

    begin
      require_relative $src_plugin_dir + '/' + file

      if $plugin_matches == nil
        next
      end

      plugin = {
          :name => $plugin_name,
          :author => $plugin_author,
          :version => $plugin_version,
          :description => $plugin_description,
          :website => $plugin_website,
          :matches => $plugin_matches,
      }

      filename = $dst_plugin_dir + '/' + file[0..-4] + ".json"
      File.open(filename, "w") do |f|
        begin
          f.puts(JSON.pretty_generate(plugin, {indent: "    "}))
        rescue Exception => e
          File.delete(filename)
        end
      end
    end
  end
end
