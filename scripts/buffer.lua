msg = require 'mp.msg'
utils = require 'mp.utils'
require 'mp.options'

--options available through --script-opts=changerefresh-[option]=value
--all of these options can be changed at runtime using profiles, the script will automatically update
local options = {
    --duration (in seconds) of the pause when changing display modes
    --set to zero to disable video pausing
    pause = 3,

    --set whether to output status messages to the osd
    osd_output = true
}

--is run whenever a change in script-opts is detected
function updateOptions(changes)
    msg.verbose('updating options')
    msg.debug(utils.to_string(changes))
end
read_options(options, 'buffer', updateOptions)


--runs the script automatically on startup if option is enabled
function buffer()
    if options.pause > 0 then
        mp.set_property_bool("pause", true)
        osdMessage('Buffering for ' .. options.pause .. " seconds")
    end

    mp.add_timeout(options.pause, function()
        mp.set_property_bool("pause", false)
    end)
end

--prints osd messages if the option is enabled
function osdMessage(string)
    if options.osd_output then
        mp.osd_message(string)
    end
end

updateOptions()

--runs the script automatically on startup if option is enabled
mp.register_event('file-loaded', buffer)
