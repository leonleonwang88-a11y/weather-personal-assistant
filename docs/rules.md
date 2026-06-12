# Weather Personal Assistant — Rules

This document defines recommendation thresholds and message templates. The application reads the JSON configuration block below at startup.

```json
{
  "temperature_unit": "celsius",
  "locations": {
    "home": { "lat": 37.7749, "lon": -122.4194, "label": "San Francisco" },
    "work": { "lat": 37.7849, "lon": -122.4094, "label": "Downtown SF" }
  },
  "default_location": "home",
  "thresholds": {
    "cold_c": 12,
    "cool_c": 18,
    "warm_c": 26,
    "hot_c": 32,
    "rain_chance_pct": 40,
    "heavy_rain_mm": 2.0,
    "windy_kmh": 30,
    "strong_wind_kmh": 50
  },
  "messages": {
    "cold": "It's cold ({temp}°C). Wear a warm jacket or coat.",
    "cool": "It's cool ({temp}°C). A light jacket or layers are a good idea.",
    "mild": "Temperature is mild ({temp}°C). Comfortable for most activities.",
    "warm": "It's warm ({temp}°C). Light clothing recommended.",
    "hot": "It's hot ({temp}°C). Stay hydrated and avoid prolonged sun exposure.",
    "rain_likely": "Rain is likely ({precip}% chance). Bring an umbrella.",
    "rain_possible": "Rain is possible ({precip}% chance). Consider a light rain layer.",
    "windy": "Windy conditions ({wind} km/h). Secure loose items outdoors.",
    "strong_wind": "Strong winds ({wind} km/h). Avoid outdoor events if possible.",
    "outdoor_ok": "Weather looks good for '{event}'.",
    "outdoor_rain": "Rain may affect outdoor event '{event}' at {time}.",
    "outdoor_wind": "Wind may affect outdoor event '{event}' at {time}.",
    "outdoor_heat": "Heat may be uncomfortable for '{event}' at {time}."
  },
  "ask_patterns": {
    "jacket": ["jacket", "coat", "cold", "wear"],
    "umbrella": ["umbrella", "rain", "wet"],
    "run": ["run", "jog", "exercise", "workout"],
    "commute": ["commute", "bike", "walk", "travel"]
  }
}
```

## Clothing Rules

| Condition | Threshold | Recommendation |
|-----------|-----------|----------------|
| Cold | ≤ `cold_c` (12°C) | Warm jacket or coat |
| Cool | `cold_c` < T ≤ `cool_c` | Light jacket or layers |
| Mild | `cool_c` < T ≤ `warm_c` | No special clothing needed |
| Warm | `warm_c` < T ≤ `hot_c` | Light clothing |
| Hot | > `hot_c` | Hydration and sun protection |

Temperature uses **apparent temperature** when available, otherwise air temperature.

## Precipitation Rules

| Condition | Threshold | Severity |
|-----------|-----------|----------|
| Rain likely | precipitation probability ≥ 40% | `warning` |
| Rain possible | 20% ≤ probability < 40% | `info` |
| Heavy rain | hourly precipitation ≥ 2.0 mm | `alert` |

## Wind Rules

| Condition | Threshold | Severity |
|-----------|-----------|----------|
| Windy | sustained wind ≥ 30 km/h | `warning` |
| Strong wind | sustained wind ≥ 50 km/h | `alert` |

## Calendar Event Rules

For events marked `"outdoor": true`:

1. Evaluate weather at the event `location` (or `default_location` if omitted) for the event start time.
2. Emit `outdoor_rain` if rain probability exceeds `rain_chance_pct`.
3. Emit `outdoor_wind` if wind exceeds `windy_kmh`.
4. Emit `outdoor_heat` if temperature exceeds `hot_c`.
5. Otherwise emit `outdoor_ok`.

## Ask Command Matching

The `ask` command uses keyword patterns from `ask_patterns`:

- **jacket** — clothing advice for current/default location
- **umbrella** — rain gear advice
- **run** — suitability for outdoor exercise (temp 5–28°C, low rain/wind)
- **commute** — combined rain, wind, and temperature summary for default location

## Severity Levels

| Level | Usage |
|-------|-------|
| `info` | Helpful context, no action required |
| `warning` | User should prepare (umbrella, layers) |
| `alert` | Significant disruption likely; consider rescheduling |
