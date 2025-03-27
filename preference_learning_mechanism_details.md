# Preference Learning Mechanism: Practical Implementation

Let me explain in more detail how the preference learning mechanism will work in practice within the Sequence Maker application:

## 1. User Feedback Collection

The preference learning cycle begins when a user provides feedback on a generated sequence:

1. **Feedback UI Integration**:
   - After the LLM generates a color sequence (using the new music analysis tools), the user can provide feedback through the UI.
   - The feedback UI includes:
     - A text field for detailed comments
     - Sentiment buttons (Like/Neutral/Dislike)
     - Optional tagging system (could be auto-generated based on text analysis)

2. **Contextual Information Capture**:
   - When feedback is submitted, we capture important context:
     - The song identifier (file path or hash)
     - The specific section(s) the feedback relates to (e.g., "Chorus 1")
     - The pattern types and colors used
     - Timestamp of when the feedback was given

3. **Storage in SQLite Database**:
   - The `PreferenceManager` stores this information in a structured format in the SQLite database.
   - Each feedback entry contains:
     ```
     {
       "id": auto_increment,
       "song_identifier": "path/to/song.mp3",
       "feedback_text": "I loved the blue pulses on the beats during the chorus",
       "sentiment": 1,  // 1=positive, 0=neutral, -1=negative
       "tags": ["chorus", "pulse", "blue", "beat_sync"],
       "created_at": "2025-03-27T10:15:00"
     }
     ```

## 2. Preference Retrieval and Processing

When the user starts a new LLM interaction for the same or a different song:

1. **Relevant Preference Selection**:
   - The `PreferenceManager.get_preference_summary()` method retrieves relevant feedback:
     - First priority: Feedback for the current song
     - Second priority: General feedback applicable to any song
     - Most recent feedback is prioritized

2. **Preference Summarization**:
   - The feedback is summarized into a concise format:
     ```
     User Preference Summary (Apply these guidelines where appropriate):
     - Song-specific preferences:
       - Likes: Blue pulses on beats during the chorus
       - Dislikes: Abrupt color transitions between sections
     - General preferences:
       - Likes: Slow color fades during verses
       - Prefers: Using brighter colors for high-energy sections
     ```

3. **Integration with LLM Context**:
   - This summary is prepended to the system message sent to the LLM.
   - The modified `send_request` method in `LLMManager` handles this automatically.

## 3. LLM Decision Influence

The LLM uses the preference summary to guide its creative decisions:

1. **Pattern Selection**:
   - If the user has expressed a preference for certain pattern types (e.g., "likes pulses on beats"), the LLM will prioritize using the `apply_beat_pattern` tool with the "pulse" pattern type.

2. **Color Selection**:
   - If the user has expressed color preferences (e.g., "prefers bright colors for high-energy sections"), the LLM will select appropriate colors for different sections.

3. **Section-Specific Treatments**:
   - The LLM can apply different treatments to different sections based on preferences (e.g., "slow fades for verses, pulses for choruses").

4. **Transition Handling**:
   - If the user has expressed preferences about transitions (e.g., "dislikes abrupt transitions"), the LLM will ensure smooth transitions between sections.

## 4. Practical Example Workflow

Here's a concrete example of how this works in practice:

1. **Initial Sequence Generation**:
   - User loads "Song A" and asks the LLM to generate a sequence.
   - LLM uses music analysis tools to understand the song structure.
   - LLM creates a sequence with various patterns.

2. **User Feedback**:
   - User provides feedback: "I like the blue pulses during the chorus, but the transition to the verse is too abrupt."
   - This is stored with sentiment +1, tags ["chorus", "pulse", "blue", "transition", "verse"].

3. **Second Generation (Same Song)**:
   - User asks for a revised sequence.
   - LLM receives the preference summary.
   - LLM maintains blue pulses for chorus but creates smoother transitions to verses.

4. **New Song Generation**:
   - User loads "Song B" and asks for a sequence.
   - LLM receives general preferences (not song-specific).
   - LLM applies the learned preference for pulse patterns in choruses and smooth transitions.

5. **Continuous Learning**:
   - As the user provides more feedback, the preference database grows.
   - The LLM receives increasingly refined guidance.
   - The system effectively "learns" the user's aesthetic preferences over time.

## 5. Technical Implementation Details

The preference learning mechanism is implemented through these key components:

1. **Database Schema**:
   ```sql
   CREATE TABLE IF NOT EXISTS preferences (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       song_identifier TEXT,
       feedback_text TEXT,
       sentiment INTEGER,
       tags TEXT,  -- Stored as JSON array
       created_at TEXT
   )
   ```

2. **Feedback Collection Method**:
   ```python
   def add_feedback(self, song_identifier, feedback_text, sentiment, tags=None):
       # Convert tags list to JSON string
       tags_json = json.dumps(tags) if tags else "[]"
       
       # Insert into database
       cursor.execute(
           "INSERT INTO preferences VALUES (NULL, ?, ?, ?, ?, ?)",
           (song_identifier, feedback_text, sentiment, tags_json, datetime.now().isoformat())
       )
   ```

3. **Preference Retrieval Method**:
   ```python
   def get_preference_summary(self, song_identifier, max_items=5):
       # Get song-specific preferences
       cursor.execute(
           "SELECT feedback_text, sentiment, tags FROM preferences WHERE song_identifier = ? ORDER BY created_at DESC LIMIT ?",
           (song_identifier, max_items)
       )
       song_preferences = cursor.fetchall()
       
       # Get general preferences if needed
       if len(song_preferences) < max_items:
           cursor.execute(
               "SELECT feedback_text, sentiment, tags FROM preferences WHERE song_identifier != ? ORDER BY created_at DESC LIMIT ?",
               (song_identifier, max_items - len(song_preferences))
           )
           general_preferences = cursor.fetchall()
       
       # Format into a summary string
       # ...
   ```

4. **LLM Integration**:
   ```python
   def send_request(self, prompt, system_message=None, ...):
       # Get preference summary
       preference_summary = self.app.preference_manager.get_preference_summary(song_identifier)
       
       # Prepend to system message
       if preference_summary:
           system_message = f"{preference_summary}\n\n{system_message}"
       
       # Send to LLM
       # ...
   ```

## 6. Advanced Features (Future Enhancements)

The preference learning system could be enhanced with these advanced features:

1. **Automatic Tagging**:
   - Use the LLM to analyze feedback text and automatically generate relevant tags.
   - Example: "I loved the blue pulses on the beats during the chorus" → ["chorus", "pulse", "blue", "positive"]

2. **Preference Conflict Resolution**:
   - When contradictory preferences exist, use recency and specificity to determine priority.
   - Example: If a user previously liked red for choruses but recently preferred blue, prioritize the more recent preference.

3. **Preference Strength Weighting**:
   - Allow users to indicate how strongly they feel about a preference.
   - Store a "strength" value (1-5) alongside sentiment.

4. **A/B Testing Interface**:
   - Present users with two alternative sequences and let them choose which they prefer.
   - This provides more structured feedback data.

5. **Preference Categories**:
   - Organize preferences into categories (colors, patterns, transitions, section treatments).
   - Allow users to view and edit their stored preferences by category.

6. **Preference Presets**:
   - Allow users to save and name specific preference combinations.
   - Example: "Energetic" preset with bright colors and strong beat synchronization.

This implementation creates a feedback loop that allows the system to continuously improve its understanding of user preferences, resulting in increasingly personalized and satisfying color sequences over time.