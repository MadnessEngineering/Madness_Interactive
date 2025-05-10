
local function calculatePosition(counter, max, rows)
    WindowManager.row = math.floor(counter / WindowManager.cols)
    local col = counter % WindowManager.cols
    local x = max.x + (col * (max.w / WindowManager.cols + WindowManager.gap))
    local y = max.y + (WindowManager.row * (max.h / rows + WindowManager.gap))
    return x, y
end
