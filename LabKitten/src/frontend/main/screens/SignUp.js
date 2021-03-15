
import React, { useState, useEffect } from 'react'
import {Input, Txt, Btn, Row, Body, Box} from '../../components/main'

const {auth, signUp, passwordReset} = require('../../functionalities/firebase')

export {SignUp}

function SignUp(){
	const [form, setForm] = useState({
		email: '', password: ''
	})
	const [user, setUser] = useState()
	useEffect(()=>{
		auth().onAuthStateChanged(()=>{
			setUser(auth().currentUser)
		})
	},[])
	function set(object){setForm(Object.assign({...form}, object))}
	
	if(user) return(
		<Body>
			<Row><Txt c='blue'>signed in as: {user.email}</Txt></Row>
			<Box h={60}></Box>
			<Row>
				<Btn on={()=>passwordReset(user)}>reset password</Btn>
				<Btn on={()=>auth().signOut()}>sign out</Btn>
			</Row>
		</Body>
	)

	return(
		<Body>
			<Input p='email' on={email=>set({email})}>{form.email}</Input>
			<Input p='password' on={password=>set({password})}>{form.password}</Input>
			<Box h={60}></Box>
			<Row>
				<Btn on={()=>passwordReset(form)}>forgot password</Btn>
				<Btn on={()=>signUp(form)}>sign up / sign in</Btn>
			</Row>
		</Body>
	)
}
