struct ColorUtils
{
    struct RGB
    {
        uint8_t red;
        uint8_t green;
        uint8_t blue;
    };

    enum class ColorIndex
    {
        Default = 0,
        Off = 1,
        White = 2,
        Warm = 3,
        Red = 4,
        Rose = 5,
        Pink = 6,
        Purple = 7,
        Amber = 8,
        Yellow = 9,
        Darkblue = 10,
        Blue = 11,
        Ice = 12,
        Cyan = 13,
        Spring = 14,
        Green = 15,
        Mint = 16,
        MaxColorIndex
    };

    enum class ColorMode {
        Mono,
        GrayScale,
        RGB,
    };

    /**
     * output: 16 bit color, bbbbbggg gggrrrrr
     */
    static uint16_t convertRGBTo16bit(uint8_t r, uint8_t g, uint8_t b)
    {
        return ((b & 0b11111) << 11) | ((g & 0b111111) << 5) | (r & 0b11111);
    }

    static uint16_t convertRGBTo16bit(RGB rgb)
    {
        return convertRGBTo16bit(rgb.red, rgb.green, rgb.blue);
    }

    static RGB convert16bitToRGB(uint16_t val)
    {
        RGB rgb;
        rgb.red = (val >> 0) & 0b11111;
        rgb.green = (val >> 5) & 0b111111;
        rgb.blue = (val >> 11) & 0b11111;
        return rgb;
    }

    /**
     * input: 6 bit color: xxrrggbb
     */
    static RGB convert6bitToRGB(uint8_t color)
    {
        RGB val;
        val.red = map((color >> 4) & 0b11, 0, 3, 0, 31);
        val.green = map((color >> 2) & 0b11, 0, 3, 0, 63);
        val.blue = map((color >> 0) & 0b11, 0, 3, 0, 31);
        return val;
    }

    static uint16_t get16bitByIdx(ColorIndex idx)
    {
        return get16bitByIdx(static_cast<uint8_t>(idx));
    }

    static uint16_t get16bitByIdx(uint8_t idx)
    {
        auto rgb = convert6bitToRGB(get6bitByIdx(idx));
        return convertRGBTo16bit(rgb);
    }

    static  uint8_t get6bitByIdx(uint8_t idx)
    {
        // 2-bit color map, 0b00RRGGBB
         uint8_t indexedColors[17] = {
            0b111111, // Default
            0, // Off
            0b111111, // White
            0b111101, // Warm White
            0b110000, // Red (Bicolor)
            0b110101, // Rose
            0b110011, // Pink
            0b010011, // Purple
            0b110100, // Amber (Bicolor)
            0b111100, // Yellow (Bicolor)
            0b000011, // Dark blue
            0b000111, // Blue
            0b011011, // Ice
            0b001111, // Cyan
            0b011100, // Spring (Bicolor)
            0b001100, // Green (Bicolor)
            0b001101, // Mint
        };

        if(idx >= sizeof(indexedColors) / sizeof(uint8_t))
        {
            return 0;
        }
        return indexedColors[idx];
    }

    static void getRGBByIdx(ColorUtils::ColorIndex idx, uint16_t &r, uint16_t &g, uint16_t &b)
    {
        if(idx >= ColorUtils::ColorIndex::MaxColorIndex)
        {
            return;
        }
        auto i = static_cast<uint8_t>(idx);
        const int k = 1365; // 2-bit color to 12 bit color conversion factor
        r = ((ColorUtils::get6bitByIdx(i) & 0b110000) >> 4) * k;
        g = ((ColorUtils::get6bitByIdx(i) & 0b1100) >> 2) * k;
        b = (ColorUtils::get6bitByIdx(i) & 0b11) * k;
    }
};