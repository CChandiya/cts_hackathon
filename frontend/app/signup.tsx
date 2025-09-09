import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, SafeAreaView, StatusBar, Image, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { Colors } from '../constants/Colors';
import { Ionicons } from '@expo/vector-icons';
import ApiService from '../services/ApiService'; // Now this will work
import AuthService from '../services/AuthService'; // Now this will work

export default function SignupScreen() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Password validation function
  const validatePassword = (password: string) => {
    const minLength = password.length >= 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
    
    return {
      isValid: minLength && hasUpperCase && hasSpecialChar,
      minLength,
      hasUpperCase,
      hasSpecialChar
    };
  };

  // Get password strength indicator
  const getPasswordStrength = (password: string) => {
    if (!password) return { strength: 'none', color: Colors.textSecondary };
    
    const validation = validatePassword(password);
    const validCount = [validation.minLength, validation.hasUpperCase, validation.hasSpecialChar].filter(Boolean).length;
    
    if (validCount === 3) return { strength: 'Strong', color: '#4CAF50' };
    if (validCount === 2) return { strength: 'Medium', color: '#FF9800' };
    return { strength: 'Weak', color: '#F44336' };
  };

  const handleSignup = async () => {
    if (!name || !email || !password) {
      Alert.alert("Error", "Please fill in all fields.");
      return;
    }

    // Validate password strength
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) {
      let errorMessage = "Password must meet the following requirements:\n";
      if (!passwordValidation.minLength) errorMessage += "• At least 8 characters\n";
      if (!passwordValidation.hasUpperCase) errorMessage += "• At least one uppercase letter\n";
      if (!passwordValidation.hasSpecialChar) errorMessage += "• At least one special character";
      
      Alert.alert("Weak Password", errorMessage);
      return;
    }

    setIsLoading(true);
    try {
      // Use the centralized ApiService
      const response = await ApiService.signup(name, email, password);
      
      if (response.ok) {
        // Use AuthService to store the new user's session token and data
        await AuthService.storeAuthData(
          response.data.session_token,
          response.data.name,
          response.data.patient_id
        );
        Alert.alert("Success", "Account created! Welcome.", [
          { text: 'Get Started', onPress: () => router.replace('/(tabs)') }
        ]);
      } else {
        Alert.alert("Signup Failed", response.data.message || "An unknown error occurred.");
      }
    } catch (error: any) {
      Alert.alert("Connection Error", "Could not connect to the server.");
    } finally {
      setIsLoading(false);
    }
  };

  const passwordStrength = getPasswordStrength(password);
  const passwordValidation = validatePassword(password);

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#E0F2F7', Colors.background]} style={StyleSheet.absoluteFill} />
      <StatusBar barStyle="dark-content" />
      <View style={styles.content}>
        <Image source={require('../assets/app-icon.png')} style={styles.logoImage} />
        <Text style={styles.title}>Create Account</Text>
        <Text style={styles.subtitle}>Start your new health journey today</Text>

        <View style={styles.inputContainer}>
          <Ionicons name="person-outline" size={22} color={Colors.textSecondary} style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Full Name"
            placeholderTextColor={Colors.textSecondary}
            value={name}
            onChangeText={setName}
            autoCapitalize="words"
          />
        </View>

        <View style={styles.inputContainer}>
          <Ionicons name="mail-outline" size={22} color={Colors.textSecondary} style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Email"
            placeholderTextColor={Colors.textSecondary}
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />
        </View>

        <View style={styles.inputContainer}>
          <Ionicons name="lock-closed-outline" size={22} color={Colors.textSecondary} style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Password"
            placeholderTextColor={Colors.textSecondary}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />
        </View>

        {/* Password Strength Indicator */}
        {password.length > 0 && (
          <View style={styles.passwordStrengthContainer}>
            <View style={styles.strengthHeader}>
              <Text style={styles.strengthLabel}>Password Strength: </Text>
              <Text style={[styles.strengthValue, { color: passwordStrength.color }]}>
                {passwordStrength.strength}
              </Text>
            </View>
            
            <View style={styles.requirementsContainer}>
              <View style={styles.requirement}>
                <Ionicons 
                  name={passwordValidation.minLength ? "checkmark-circle" : "close-circle"} 
                  size={16} 
                  color={passwordValidation.minLength ? "#4CAF50" : "#F44336"} 
                />
                <Text style={[styles.requirementText, { 
                  color: passwordValidation.minLength ? "#4CAF50" : Colors.textSecondary 
                }]}>
                  At least 8 characters
                </Text>
              </View>
              
              <View style={styles.requirement}>
                <Ionicons 
                  name={passwordValidation.hasUpperCase ? "checkmark-circle" : "close-circle"} 
                  size={16} 
                  color={passwordValidation.hasUpperCase ? "#4CAF50" : "#F44336"} 
                />
                <Text style={[styles.requirementText, { 
                  color: passwordValidation.hasUpperCase ? "#4CAF50" : Colors.textSecondary 
                }]}>
                  One uppercase letter
                </Text>
              </View>
              
              <View style={styles.requirement}>
                <Ionicons 
                  name={passwordValidation.hasSpecialChar ? "checkmark-circle" : "close-circle"} 
                  size={16} 
                  color={passwordValidation.hasSpecialChar ? "#4CAF50" : "#F44336"} 
                />
                <Text style={[styles.requirementText, { 
                  color: passwordValidation.hasSpecialChar ? "#4CAF50" : Colors.textSecondary 
                }]}>
                  One special character
                </Text>
              </View>
            </View>
          </View>
        )}

        <TouchableOpacity style={styles.button} onPress={handleSignup} disabled={isLoading}>
          {isLoading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.buttonText}>Create Account</Text>}
        </TouchableOpacity>

        <View style={styles.loginContainer}>
          <Text style={styles.loginText}>Already have an account? </Text>
          <TouchableOpacity onPress={() => router.push('/login')}>
            <Text style={styles.loginLink}>Log In</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: 'transparent'
  },
  logoImage: {
    width: 100,
    height: 100,
    resizeMode: 'contain',
    marginBottom: 20,
    alignSelf: 'center'
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: Colors.text,
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginBottom: 30,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E8E8E8',
    paddingHorizontal: 15,
    marginBottom: 15,
  },
  inputError: {
    borderColor: '#F44336',
    borderWidth: 1.5,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    height: 55,
    fontSize: 16,
    color: Colors.text,
  },
  emailErrorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: -10,
    marginBottom: 15,
    paddingHorizontal: 5,
    gap: 5,
  },
  emailErrorText: {
    fontSize: 12,
    color: '#F44336',
    flex: 1,
  },
  passwordStrengthContainer: {
    marginBottom: 20,
    padding: 12,
    backgroundColor: Colors.surface,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E8E8E8',
  },
  strengthHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  strengthLabel: {
    fontSize: 14,
    color: Colors.text,
    fontWeight: '500',
  },
  strengthValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  requirementsContainer: {
    gap: 4,
  },
  requirement: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  requirementText: {
    fontSize: 12,
    flex: 1,
  },
  button: {
    backgroundColor: Colors.primary,
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
    width: '100%',
    minHeight: 60,
    marginTop: 10,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold'
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 25,
  },
  loginText: {
    fontSize: 14,
    color: Colors.textSecondary,
  },
  loginLink: {
    fontSize: 14,
    color: Colors.primary,
    fontWeight: 'bold',
  }
});